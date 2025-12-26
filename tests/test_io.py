"""
Tests for input/output functionality.

This module tests:
- Data validation functions
- JSON loading and saving
- CSV loading and saving
- Metadata handling
- Export functions (hydrostatics, stability, reports)
- Error handling
"""

import pytest
import json
import csv
import numpy as np
from pathlib import Path
import tempfile
import shutil

from src.io import (
    load_hull_from_json,
    load_hull_from_csv,
    save_hull_to_json,
    save_hull_to_csv,
    validate_hull_data,
    validate_metadata,
    validate_profile_data,
    validate_point_data,
    validate_csv_data,
    validate_symmetry,
    get_default_metadata,
    apply_metadata_defaults,
    create_metadata_template,
    merge_metadata,
    extract_metadata_from_comments,
    format_metadata_for_display,
    DataLoadError,
    export_hydrostatic_properties,
    export_stability_curve,
    export_stability_metrics,
    export_righting_arm,
    export_cg_summary,
    export_cross_sections,
    export_waterline_comparison,
    generate_hydrostatic_report,
    generate_stability_report,
    generate_complete_report,
)
from src.geometry.hull import KayakHull
from src.geometry.profile import Profile
from src.geometry.point import Point3D
from src.hydrostatics import CenterOfGravity, calculate_center_of_buoyancy
from src.stability import StabilityAnalyzer, calculate_gz_curve


class TestValidateMetadata:
    """Tests for metadata validation."""
    
    def test_valid_metadata(self):
        """Test validation of valid metadata."""
        metadata = {
            'units': 'm',
            'coordinate_system': 'centerline_origin',
            'water_density': 1025.0
        }
        is_valid, errors = validate_metadata(metadata)
        assert is_valid
        assert len(errors) == 0
    
    def test_missing_required_field(self):
        """Test validation catches missing required fields."""
        metadata = {
            'units': 'm',
            # Missing coordinate_system and water_density
        }
        is_valid, errors = validate_metadata(metadata)
        assert not is_valid
        assert any('coordinate_system' in err for err in errors)
        assert any('water_density' in err for err in errors)
    
    def test_invalid_units(self):
        """Test validation catches invalid units."""
        metadata = {
            'units': 'invalid_unit',
            'coordinate_system': 'centerline_origin',
            'water_density': 1025.0
        }
        is_valid, errors = validate_metadata(metadata)
        assert not is_valid
        assert any('unit' in err.lower() for err in errors)
    
    def test_invalid_coordinate_system(self):
        """Test validation catches invalid coordinate system."""
        metadata = {
            'units': 'm',
            'coordinate_system': 'invalid_system',
            'water_density': 1025.0
        }
        is_valid, errors = validate_metadata(metadata)
        assert not is_valid
        assert any('coordinate' in err.lower() for err in errors)
    
    def test_negative_water_density(self):
        """Test validation catches negative water density."""
        metadata = {
            'units': 'm',
            'coordinate_system': 'centerline_origin',
            'water_density': -1000.0
        }
        is_valid, errors = validate_metadata(metadata)
        assert not is_valid
        assert any('density' in err.lower() and 'positive' in err.lower() for err in errors)
    
    def test_non_numeric_water_density(self):
        """Test validation catches non-numeric water density."""
        metadata = {
            'units': 'm',
            'coordinate_system': 'centerline_origin',
            'water_density': 'not_a_number'
        }
        is_valid, errors = validate_metadata(metadata)
        assert not is_valid
        assert any('density' in err.lower() and 'number' in err.lower() for err in errors)
    
    def test_optional_fields(self):
        """Test that optional fields don't cause validation to fail."""
        metadata = {
            'units': 'm',
            'coordinate_system': 'centerline_origin',
            'water_density': 1025.0,
            'name': 'Test Kayak',
            'description': 'A test kayak',
            'length': 5.0,
            'beam': 0.6
        }
        is_valid, errors = validate_metadata(metadata)
        assert is_valid
        assert len(errors) == 0


class TestValidatePointData:
    """Tests for point data validation."""
    
    def test_valid_point(self):
        """Test validation of valid point."""
        point = {'x': 0.0, 'y': 1.0, 'z': 2.0}
        is_valid, errors = validate_point_data(point)
        assert is_valid
        assert len(errors) == 0
    
    def test_missing_coordinate(self):
        """Test validation catches missing coordinates."""
        point = {'x': 0.0, 'y': 1.0}  # Missing z
        is_valid, errors = validate_point_data(point)
        assert not is_valid
        assert any('z' in err.lower() for err in errors)
    
    def test_non_numeric_coordinate(self):
        """Test validation catches non-numeric coordinates."""
        point = {'x': 0.0, 'y': 'not_a_number', 'z': 2.0}
        is_valid, errors = validate_point_data(point)
        assert not is_valid
        assert any('y' in err.lower() and 'numeric' in err.lower() for err in errors)
    
    def test_infinite_coordinate(self):
        """Test validation catches infinite coordinates."""
        point = {'x': 0.0, 'y': float('inf'), 'z': 2.0}
        is_valid, errors = validate_point_data(point)
        assert not is_valid
        assert any('y' in err.lower() and 'finite' in err.lower() for err in errors)
    
    def test_nan_coordinate(self):
        """Test validation catches NaN coordinates."""
        point = {'x': 0.0, 'y': float('nan'), 'z': 2.0}
        is_valid, errors = validate_point_data(point)
        assert not is_valid
        assert any('y' in err.lower() for err in errors)


class TestValidateProfileData:
    """Tests for profile data validation."""
    
    def test_valid_profile(self):
        """Test validation of valid profile."""
        profile = {
            'station': 0.0,
            'points': [
                {'x': 0.0, 'y': 0.0, 'z': 1.0},
                {'x': 0.0, 'y': 1.0, 'z': 0.5},
                {'x': 0.0, 'y': -1.0, 'z': 0.5}
            ]
        }
        is_valid, errors = validate_profile_data(profile)
        assert is_valid
        assert len(errors) == 0
    
    def test_missing_station(self):
        """Test validation catches missing station."""
        profile = {
            'points': [
                {'x': 0.0, 'y': 0.0, 'z': 1.0},
                {'x': 0.0, 'y': 1.0, 'z': 0.5},
                {'x': 0.0, 'y': -1.0, 'z': 0.5}
            ]
        }
        is_valid, errors = validate_profile_data(profile)
        assert not is_valid
        assert any('station' in err.lower() for err in errors)
    
    def test_missing_points(self):
        """Test validation catches missing points."""
        profile = {'station': 0.0}
        is_valid, errors = validate_profile_data(profile)
        assert not is_valid
        assert any('points' in err.lower() for err in errors)
    
    def test_too_few_points(self):
        """Test validation catches too few points."""
        profile = {
            'station': 0.0,
            'points': [
                {'x': 0.0, 'y': 0.0, 'z': 1.0},
                {'x': 0.0, 'y': 1.0, 'z': 0.5}
            ]
        }
        is_valid, errors = validate_profile_data(profile)
        assert not is_valid
        assert any('at least' in err.lower() for err in errors)
    
    def test_inconsistent_x_coordinate(self):
        """Test validation catches inconsistent x coordinates."""
        profile = {
            'station': 0.0,
            'points': [
                {'x': 0.0, 'y': 0.0, 'z': 1.0},
                {'x': 1.0, 'y': 1.0, 'z': 0.5},  # Wrong x
                {'x': 0.0, 'y': -1.0, 'z': 0.5}
            ]
        }
        is_valid, errors = validate_profile_data(profile)
        assert not is_valid
        assert any('doesn\'t match station' in err.lower() for err in errors)


class TestValidateHullData:
    """Tests for complete hull data validation."""
    
    def test_valid_hull(self):
        """Test validation of valid hull data."""
        hull_data = {
            'metadata': {
                'units': 'm',
                'coordinate_system': 'centerline_origin',
                'water_density': 1025.0
            },
            'profiles': [
                {
                    'station': 0.0,
                    'points': [
                        {'x': 0.0, 'y': 0.0, 'z': 1.0},
                        {'x': 0.0, 'y': 1.0, 'z': 0.5},
                        {'x': 0.0, 'y': -1.0, 'z': 0.5}
                    ]
                },
                {
                    'station': 1.0,
                    'points': [
                        {'x': 1.0, 'y': 0.0, 'z': 1.0},
                        {'x': 1.0, 'y': 1.0, 'z': 0.5},
                        {'x': 1.0, 'y': -1.0, 'z': 0.5}
                    ]
                }
            ]
        }
        is_valid, errors = validate_hull_data(hull_data)
        assert is_valid
        assert len(errors) == 0
    
    def test_missing_profiles(self):
        """Test validation catches missing profiles."""
        hull_data = {
            'metadata': {
                'units': 'm',
                'coordinate_system': 'centerline_origin',
                'water_density': 1025.0
            }
        }
        is_valid, errors = validate_hull_data(hull_data)
        assert not is_valid
        assert any('profiles' in err.lower() for err in errors)
    
    def test_too_few_profiles(self):
        """Test validation catches too few profiles."""
        hull_data = {
            'metadata': {
                'units': 'm',
                'coordinate_system': 'centerline_origin',
                'water_density': 1025.0
            },
            'profiles': [
                {
                    'station': 0.0,
                    'points': [
                        {'x': 0.0, 'y': 0.0, 'z': 1.0},
                        {'x': 0.0, 'y': 1.0, 'z': 0.5},
                        {'x': 0.0, 'y': -1.0, 'z': 0.5}
                    ]
                }
            ]
        }
        is_valid, errors = validate_hull_data(hull_data)
        assert not is_valid
        assert any('at least' in err.lower() and 'profiles' in err.lower() for err in errors)
    
    def test_duplicate_stations(self):
        """Test validation catches duplicate stations."""
        hull_data = {
            'metadata': {
                'units': 'm',
                'coordinate_system': 'centerline_origin',
                'water_density': 1025.0
            },
            'profiles': [
                {
                    'station': 0.0,
                    'points': [
                        {'x': 0.0, 'y': 0.0, 'z': 1.0},
                        {'x': 0.0, 'y': 1.0, 'z': 0.5},
                        {'x': 0.0, 'y': -1.0, 'z': 0.5}
                    ]
                },
                {
                    'station': 0.0,  # Duplicate
                    'points': [
                        {'x': 0.0, 'y': 0.0, 'z': 1.0},
                        {'x': 0.0, 'y': 1.0, 'z': 0.5},
                        {'x': 0.0, 'y': -1.0, 'z': 0.5}
                    ]
                }
            ]
        }
        is_valid, errors = validate_hull_data(hull_data)
        assert not is_valid
        assert any('duplicate' in err.lower() for err in errors)


class TestValidateCSVData:
    """Tests for CSV data validation."""
    
    def test_valid_csv_data(self):
        """Test validation of valid CSV data."""
        data = [[0.0, 0.0, 1.0], [0.0, 1.0, 0.5], [0.0, -1.0, 0.5]]
        is_valid, errors = validate_csv_data(data, ['x', 'y', 'z'])
        assert is_valid
        assert len(errors) == 0
    
    def test_wrong_number_of_columns(self):
        """Test validation catches wrong number of columns."""
        data = [[0.0, 0.0], [0.0, 1.0]]  # Only 2 columns
        is_valid, errors = validate_csv_data(data, ['x', 'y', 'z'])
        assert not is_valid
        assert any('columns' in err.lower() for err in errors)
    
    def test_nan_values(self):
        """Test validation catches NaN values."""
        data = [[0.0, float('nan'), 1.0], [0.0, 1.0, 0.5]]
        is_valid, errors = validate_csv_data(data, ['x', 'y', 'z'])
        assert not is_valid
        assert any('nan' in err.lower() for err in errors)
    
    def test_infinite_values(self):
        """Test validation catches infinite values."""
        data = [[0.0, float('inf'), 1.0], [0.0, 1.0, 0.5]]
        is_valid, errors = validate_csv_data(data, ['x', 'y', 'z'])
        assert not is_valid
        assert any('infinite' in err.lower() for err in errors)


class TestValidateSymmetry:
    """Tests for symmetry validation."""
    
    def test_symmetric_points(self):
        """Test validation of symmetric points."""
        points = [
            {'x': 0.0, 'y': 0.0, 'z': 1.0},
            {'x': 0.0, 'y': 0.5, 'z': 0.5},
            {'x': 0.0, 'y': -0.5, 'z': 0.5}
        ]
        is_sym, errors = validate_symmetry(points)
        assert is_sym
        assert len(errors) == 0
    
    def test_asymmetric_points(self):
        """Test validation catches asymmetry."""
        points = [
            {'x': 0.0, 'y': 0.0, 'z': 1.0},
            {'x': 0.0, 'y': 0.5, 'z': 0.5},
            # Missing matching point at y=-0.5
        ]
        is_sym, errors = validate_symmetry(points)
        assert not is_sym
        assert len(errors) > 0


class TestDefaultMetadata:
    """Tests for default metadata functions."""
    
    def test_get_default_metadata(self):
        """Test getting default metadata."""
        defaults = get_default_metadata()
        assert 'units' in defaults
        assert 'coordinate_system' in defaults
        assert 'water_density' in defaults
    
    def test_apply_metadata_defaults_empty(self):
        """Test applying defaults to empty metadata."""
        result = apply_metadata_defaults(None)
        assert 'units' in result
        assert 'coordinate_system' in result
        assert 'water_density' in result
    
    def test_apply_metadata_defaults_override(self):
        """Test that user values override defaults."""
        user_meta = {'units': 'ft', 'name': 'MyKayak'}
        result = apply_metadata_defaults(user_meta)
        assert result['units'] == 'ft'
        assert result['name'] == 'MyKayak'
        assert 'coordinate_system' in result  # From defaults
    
    def test_create_metadata_template(self):
        """Test creating metadata template."""
        template = create_metadata_template()
        assert 'units' in template
        assert 'name' in template
    
    def test_merge_metadata(self):
        """Test merging metadata dictionaries."""
        base = {'units': 'm', 'name': 'Base'}
        override = {'name': 'Override', 'description': 'New'}
        result = merge_metadata(base, override)
        assert result['units'] == 'm'
        assert result['name'] == 'Override'
        assert result['description'] == 'New'
    
    def test_extract_metadata_from_comments(self):
        """Test extracting metadata from comment lines."""
        comments = [
            '# Units: m',
            '# Water density: 1000',
            '# Coordinate system: centerline_origin'
        ]
        meta = extract_metadata_from_comments(comments)
        assert meta['units'] == 'm'
        assert meta['water_density'] == 1000.0
        assert meta['coordinate_system'] == 'centerline_origin'
    
    def test_format_metadata_for_display(self):
        """Test formatting metadata for display."""
        meta = {'name': 'TestKayak', 'units': 'm', 'water_density': 1025.0}
        formatted = format_metadata_for_display(meta)
        assert 'name' in formatted.lower()
        assert 'TestKayak' in formatted


class TestLoadHullFromJSON:
    """Tests for loading hull from JSON files."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for test files."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    def test_load_valid_json(self, temp_dir):
        """Test loading a valid JSON file."""
        # Create test JSON file
        hull_data = {
            'metadata': {
                'units': 'm',
                'coordinate_system': 'centerline_origin',
                'water_density': 1025.0
            },
            'profiles': [
                {
                    'station': 0.0,
                    'points': [
                        {'x': 0.0, 'y': 0.0, 'z': 1.0},
                        {'x': 0.0, 'y': 0.5, 'z': 0.5},
                        {'x': 0.0, 'y': -0.5, 'z': 0.5}
                    ]
                },
                {
                    'station': 1.0,
                    'points': [
                        {'x': 1.0, 'y': 0.0, 'z': 1.0},
                        {'x': 1.0, 'y': 0.5, 'z': 0.5},
                        {'x': 1.0, 'y': -0.5, 'z': 0.5}
                    ]
                }
            ]
        }
        
        filepath = Path(temp_dir) / 'test_hull.json'
        with open(filepath, 'w') as f:
            json.dump(hull_data, f)
        
        # Load the hull
        hull = load_hull_from_json(filepath)
        
        # Verify
        assert isinstance(hull, KayakHull)
        assert len(hull.get_stations()) == 2
        assert 0.0 in hull.get_stations()
        assert 1.0 in hull.get_stations()
    
    def test_load_file_not_found(self):
        """Test error when file doesn't exist."""
        with pytest.raises(FileNotFoundError):
            load_hull_from_json('nonexistent_file.json')
    
    def test_load_invalid_json(self, temp_dir):
        """Test error with invalid JSON."""
        filepath = Path(temp_dir) / 'invalid.json'
        with open(filepath, 'w') as f:
            f.write('{ invalid json }')
        
        with pytest.raises(DataLoadError):
            load_hull_from_json(filepath)
    
    def test_load_invalid_hull_data(self, temp_dir):
        """Test error with invalid hull data."""
        hull_data = {
            'metadata': {'units': 'invalid_unit'},  # Invalid
            'profiles': []  # Too few profiles
        }
        
        filepath = Path(temp_dir) / 'invalid_hull.json'
        with open(filepath, 'w') as f:
            json.dump(hull_data, f)
        
        with pytest.raises(DataLoadError):
            load_hull_from_json(filepath)
    
    def test_load_sample_files(self):
        """Test loading the actual sample files."""
        # Test simple hull
        hull = load_hull_from_json('data/sample_hull_simple.json')
        assert isinstance(hull, KayakHull)
        assert len(hull.get_stations()) >= 2
        
        # Test kayak hull
        hull = load_hull_from_json('data/sample_hull_kayak.json')
        assert isinstance(hull, KayakHull)
        assert len(hull.get_stations()) >= 2


class TestLoadHullFromCSV:
    """Tests for loading hull from CSV files."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for test files."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    def test_load_valid_csv_xyz(self, temp_dir):
        """Test loading a valid CSV file in xyz format."""
        csv_content = """# Units: m
x,y,z
0.0,0.0,1.0
0.0,0.5,0.5
0.0,-0.5,0.5
1.0,0.0,1.0
1.0,0.5,0.5
1.0,-0.5,0.5
"""
        filepath = Path(temp_dir) / 'test.csv'
        with open(filepath, 'w') as f:
            f.write(csv_content)
        
        hull = load_hull_from_csv(filepath, format_type='xyz')
        
        assert isinstance(hull, KayakHull)
        assert len(hull.get_stations()) == 2
    
    def test_load_valid_csv_station_yz(self, temp_dir):
        """Test loading a valid CSV file in station_yz format."""
        csv_content = """station,y,z
0.0,0.0,1.0
0.0,0.5,0.5
0.0,-0.5,0.5
1.0,0.0,1.0
1.0,0.5,0.5
1.0,-0.5,0.5
"""
        filepath = Path(temp_dir) / 'test.csv'
        with open(filepath, 'w') as f:
            f.write(csv_content)
        
        hull = load_hull_from_csv(filepath, format_type='station_yz')
        
        assert isinstance(hull, KayakHull)
        assert len(hull.get_stations()) == 2
    
    def test_load_csv_with_metadata_comments(self, temp_dir):
        """Test that metadata is extracted from CSV comments."""
        csv_content = """# Units: ft
# Water density: 1000.0
# Coordinate system: centerline_origin
x,y,z
0.0,0.0,1.0
0.0,0.5,0.5
0.0,-0.5,0.5
1.0,0.0,1.0
1.0,0.5,0.5
1.0,-0.5,0.5
"""
        filepath = Path(temp_dir) / 'test.csv'
        with open(filepath, 'w') as f:
            f.write(csv_content)
        
        hull = load_hull_from_csv(filepath)
        
        assert hull.metadata['units'] == 'ft'
        assert hull.metadata['water_density'] == 1000.0
    
    def test_load_csv_invalid_format_type(self, temp_dir):
        """Test error with invalid format type."""
        csv_content = """x,y,z
0.0,0.0,1.0
"""
        filepath = Path(temp_dir) / 'test.csv'
        with open(filepath, 'w') as f:
            f.write(csv_content)
        
        with pytest.raises(ValueError):
            load_hull_from_csv(filepath, format_type='invalid')
    
    def test_load_sample_csv(self):
        """Test loading the actual sample CSV file."""
        hull = load_hull_from_csv('data/sample_hull_simple.csv')
        assert isinstance(hull, KayakHull)
        assert len(hull.get_stations()) >= 2


class TestSaveHull:
    """Tests for saving hull to files."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for test files."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def sample_hull(self):
        """Create a sample hull for testing."""
        hull = KayakHull()
        
        # Add two profiles
        profile1 = Profile(0.0, [
            Point3D(0.0, 0.0, 1.0),
            Point3D(0.0, 0.5, 0.5),
            Point3D(0.0, -0.5, 0.5)
        ])
        profile2 = Profile(1.0, [
            Point3D(1.0, 0.0, 1.0),
            Point3D(1.0, 0.5, 0.5),
            Point3D(1.0, -0.5, 0.5)
        ])
        
        hull.add_profile(profile1)
        hull.add_profile(profile2)
        
        return hull
    
    def test_save_and_load_json(self, temp_dir, sample_hull):
        """Test saving to JSON and loading back."""
        filepath = Path(temp_dir) / 'output.json'
        metadata = {'name': 'Test Kayak', 'units': 'm'}
        
        save_hull_to_json(sample_hull, filepath, metadata)
        
        # Load it back
        loaded_hull = load_hull_from_json(filepath)
        
        # Verify
        assert len(loaded_hull.get_stations()) == len(sample_hull.get_stations())
    
    def test_save_and_load_csv(self, temp_dir, sample_hull):
        """Test saving to CSV and loading back."""
        filepath = Path(temp_dir) / 'output.csv'
        metadata = {'units': 'm'}
        
        save_hull_to_csv(sample_hull, filepath, format_type='xyz', metadata=metadata)
        
        # Load it back
        loaded_hull = load_hull_from_csv(filepath, format_type='xyz')
        
        # Verify
        assert len(loaded_hull.get_stations()) == len(sample_hull.get_stations())


class TestIntegration:
    """Integration tests for complete workflows."""
    
    def test_load_json_perform_calculation(self):
        """Test loading JSON and performing calculations."""
        hull = load_hull_from_json('data/sample_hull_simple.json')
        
        # Verify we can get profiles
        stations = hull.get_stations()
        assert len(stations) >= 2
        
        # Verify we can get a profile
        profile = hull.get_profile(stations[0])
        assert profile is not None
        assert len(profile.points) >= 3
    
    def test_load_csv_perform_calculation(self):
        """Test loading CSV and performing calculations."""
        hull = load_hull_from_csv('data/sample_hull_simple.csv')
        
        # Verify we can get profiles
        stations = hull.get_stations()
        assert len(stations) >= 2
        
        # Verify we can get a profile
        profile = hull.get_profile(stations[0])
        assert profile is not None
        assert len(profile.points) >= 3


class TestExportHydrostatics:
    """Tests for hydrostatic property exports."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for test outputs."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def sample_hull(self):
        """Create a simple test hull."""
        hull = KayakHull()
        for x_pos in [0.0, 1.0, 2.0]:
            points = [
                Point3D(x_pos, 0.0, 0.5),
                Point3D(x_pos, 0.3, 0.0),
                Point3D(x_pos, -0.3, 0.0),
            ]
            hull.add_profile(Profile(station=x_pos, points=points))
        return hull
    
    @pytest.fixture
    def sample_cb(self, sample_hull):
        """Create a sample center of buoyancy."""
        return calculate_center_of_buoyancy(sample_hull, waterline_z=0.2)
    
    def test_export_hydrostatic_properties(self, temp_dir, sample_cb):
        """Test exporting hydrostatic properties to CSV."""
        filepath = Path(temp_dir) / 'hydrostatics.csv'
        export_hydrostatic_properties(sample_cb, filepath)
        
        # Verify file exists
        assert filepath.exists()
        
        # Read and verify content
        with open(filepath, 'r') as f:
            lines = f.readlines()
            # Should have metadata comments
            assert any(line.startswith('#') for line in lines)
            # Should have data rows
            data_lines = [line for line in lines if not line.startswith('#') and line.strip()]
            assert len(data_lines) > 1  # Header + data rows
    
    def test_export_hydrostatic_with_metadata(self, temp_dir, sample_cb):
        """Test exporting with custom metadata."""
        filepath = Path(temp_dir) / 'hydrostatics_meta.csv'
        metadata = {'hull_name': 'Test Kayak', 'description': 'Test export'}
        export_hydrostatic_properties(sample_cb, filepath, metadata=metadata)
        
        # Read and verify metadata in comments
        with open(filepath, 'r') as f:
            content = f.read()
            assert 'Test Kayak' in content
    
    def test_export_creates_directory(self, temp_dir, sample_cb):
        """Test that export creates necessary directories."""
        filepath = Path(temp_dir) / 'subdir' / 'nested' / 'hydrostatics.csv'
        export_hydrostatic_properties(sample_cb, filepath)
        
        assert filepath.exists()
        assert filepath.parent.exists()


class TestExportStability:
    """Tests for stability curve and metrics exports."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for test outputs."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def sample_hull(self):
        """Create a simple test hull."""
        hull = KayakHull()
        for x_pos in np.linspace(0, 4, 5):
            points = [
                Point3D(x_pos, 0.0, 0.5),
                Point3D(x_pos, 0.4, -0.3),
                Point3D(x_pos, -0.4, -0.3),
            ]
            hull.add_profile(Profile(station=x_pos, points=points))
        return hull
    
    @pytest.fixture
    def sample_cg(self):
        """Create a sample CG."""
        return CenterOfGravity(lcg=2.0, vcg=-0.2, tcg=0.0, total_mass=80.0, num_components=1)
    
    @pytest.fixture
    def sample_analyzer(self, sample_hull, sample_cg):
        """Create a sample analyzer."""
        return StabilityAnalyzer(sample_hull, sample_cg, waterline_z=0.2)
    
    def test_export_stability_curve(self, temp_dir, sample_analyzer):
        """Test exporting stability curve to CSV."""
        curve = sample_analyzer.generate_stability_curve(max_angle=60)
        filepath = Path(temp_dir) / 'stability_curve.csv'
        
        export_stability_curve(curve, filepath)
        
        # Verify file exists
        assert filepath.exists()
        
        # Read and verify content
        with open(filepath, 'r') as f:
            reader = csv.reader(f)
            lines = list(reader)
            # Find header (after comments)
            header_idx = next(i for i, line in enumerate(lines) if 'Heel_Angle' in line[0])
            header = lines[header_idx]
            data_lines = lines[header_idx + 1:]
            
            # Verify header
            assert 'Heel_Angle_deg' in header
            assert 'GZ_m' in header
            assert 'LCB_m' in header  # Default includes CB
            
            # Verify data
            assert len(data_lines) > 0
            # Check first data row is numeric
            assert all(val.replace('.', '').replace('-', '').isdigit() for val in data_lines[0])
    
    def test_export_stability_curve_without_cb(self, temp_dir, sample_analyzer):
        """Test exporting stability curve without CB data."""
        curve = sample_analyzer.generate_stability_curve()
        filepath = Path(temp_dir) / 'stability_curve_no_cb.csv'
        
        export_stability_curve(curve, filepath, include_cb=False)
        
        # Read and verify
        with open(filepath, 'r') as f:
            reader = csv.reader(f)
            lines = list(reader)
            header_idx = next(i for i, line in enumerate(lines) if 'Heel_Angle' in line[0])
            header = lines[header_idx]
            
            # Should not have CB columns
            assert 'LCB_m' not in header
            assert len(header) == 2  # Only angle and GZ
    
    def test_export_stability_metrics(self, temp_dir, sample_analyzer):
        """Test exporting stability metrics to CSV."""
        metrics = sample_analyzer.analyze_stability()
        filepath = Path(temp_dir) / 'stability_metrics.csv'
        
        export_stability_metrics(metrics, filepath)
        
        # Verify file exists
        assert filepath.exists()
        
        # Read and verify content
        with open(filepath, 'r') as f:
            content = f.read()
            # Should contain key metrics
            assert 'GM' in content or 'Metacentric' in content
            assert 'Maximum GZ' in content
            assert 'Range' in content or 'Positive Stability' in content
    
    def test_export_righting_arm(self, temp_dir, sample_analyzer):
        """Test exporting single righting arm calculation."""
        ra = sample_analyzer.calculate_righting_arm(30.0)
        filepath = Path(temp_dir) / 'righting_arm_30deg.csv'
        
        export_righting_arm(ra, filepath)
        
        # Verify file exists
        assert filepath.exists()
        
        # Read and verify content
        with open(filepath, 'r') as f:
            content = f.read()
            assert '30' in content  # Heel angle
            assert 'GZ' in content
            assert 'Center of Buoyancy' in content


class TestExportCG:
    """Tests for center of gravity exports."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for test outputs."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    def test_export_cg_summary_single_component(self, temp_dir):
        """Test exporting CG with single component."""
        cg = CenterOfGravity(lcg=2.5, vcg=-0.3, tcg=0.0, total_mass=100.0, num_components=1)
        filepath = Path(temp_dir) / 'cg_summary.csv'
        
        export_cg_summary(cg, filepath)
        
        # Verify file exists
        assert filepath.exists()
        
        # Read and verify content
        with open(filepath, 'r') as f:
            content = f.read()
            assert '2.5' in content  # LCG
            assert '100' in content  # Mass
    
    def test_export_cg_summary_multiple_components(self, temp_dir):
        """Test exporting CG with multiple components."""
        # Create CG with manual components
        cg = CenterOfGravity(
            lcg=2.44,
            vcg=-0.36,
            tcg=0.0,
            total_mass=100.0,
            num_components=2,
            components=[
                {'name': 'Kayak', 'mass': 20.0, 'lcg': 2.5, 'vcg': -0.1, 'tcg': 0.0},
                {'name': 'Paddler', 'mass': 80.0, 'lcg': 2.4, 'vcg': -0.4, 'tcg': 0.0}
            ]
        )
        filepath = Path(temp_dir) / 'cg_components.csv'
        
        export_cg_summary(cg, filepath, include_components=True)
        
        # Read and verify content
        with open(filepath, 'r') as f:
            content = f.read()
            assert 'Kayak' in content
            assert 'Paddler' in content
            assert 'Component Breakdown' in content


class TestExportCrossSections:
    """Tests for cross-section data exports."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for test outputs."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def sample_hull(self):
        """Create a simple test hull."""
        hull = KayakHull()
        for x_pos in np.linspace(0, 4, 7):
            points = [
                Point3D(x_pos, 0.0, 0.5),
                Point3D(x_pos, 0.4, 0.0),
                Point3D(x_pos, -0.4, 0.0),
            ]
            hull.add_profile(Profile(station=x_pos, points=points))
        return hull
    
    def test_export_cross_sections(self, temp_dir, sample_hull):
        """Test exporting cross-sectional properties."""
        filepath = Path(temp_dir) / 'cross_sections.csv'
        export_cross_sections(sample_hull, waterline_z=-0.1, filepath=filepath)
        
        # Verify file exists
        assert filepath.exists()
        
        # Read and verify content
        with open(filepath, 'r') as f:
            reader = csv.reader(f)
            lines = list(reader)
            # Find header (skip comment lines starting with #)
            header_idx = next(i for i, line in enumerate(lines) if line and not line[0].startswith('#') and 'Station' in line[0])
            header = lines[header_idx]
            data_lines = lines[header_idx + 1:]
            
            # Verify header
            assert 'Station_m' in header
            assert 'Area_m2' in header
            assert 'Centroid_Y_m' in header
            assert 'Centroid_Z_m' in header
            
            # Verify data rows exist
            assert len(data_lines) > 0


class TestReportGeneration:
    """Tests for report generation."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for test outputs."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def sample_hull(self):
        """Create a simple test hull."""
        hull = KayakHull()
        for x_pos in np.linspace(0, 4, 5):
            points = [
                Point3D(x_pos, 0.0, 0.5),
                Point3D(x_pos, 0.4, -0.3),
                Point3D(x_pos, -0.4, -0.3),
            ]
            hull.add_profile(Profile(station=x_pos, points=points))
        return hull
    
    @pytest.fixture
    def sample_cg(self):
        """Create a sample CG."""
        return CenterOfGravity(lcg=2.0, vcg=-0.2, tcg=0.0, total_mass=80.0, num_components=1)
    
    @pytest.fixture
    def sample_cb(self, sample_hull):
        """Create a sample CB."""
        return calculate_center_of_buoyancy(sample_hull, waterline_z=0.2)
    
    @pytest.fixture
    def sample_analyzer(self, sample_hull, sample_cg):
        """Create a sample analyzer."""
        return StabilityAnalyzer(sample_hull, sample_cg, waterline_z=0.2)
    
    def test_generate_hydrostatic_report(self, temp_dir, sample_hull, sample_cb):
        """Test generating hydrostatic report."""
        filepath = Path(temp_dir) / 'hydrostatic_report.md'
        generate_hydrostatic_report(sample_hull, sample_cb, filepath)
        
        # Verify file exists
        assert filepath.exists()
        
        # Read and verify content
        with open(filepath, 'r') as f:
            content = f.read()
            # Should be markdown format
            assert '# Hydrostatic Analysis Report' in content
            assert '## Hydrostatic Properties' in content
            assert 'Volume' in content
            assert 'Displacement' in content
            assert 'Center of Buoyancy' in content
    
    def test_generate_stability_report(self, temp_dir, sample_analyzer):
        """Test generating stability report."""
        curve = sample_analyzer.generate_stability_curve()
        metrics = sample_analyzer.analyze_stability()
        filepath = Path(temp_dir) / 'stability_report.md'
        
        generate_stability_report(curve, metrics, filepath)
        
        # Verify file exists
        assert filepath.exists()
        
        # Read and verify content
        with open(filepath, 'r') as f:
            content = f.read()
            assert '# Stability Analysis Report' in content
            assert '## Stability Metrics' in content
            assert 'GM' in content
            assert 'Maximum GZ' in content
    
    def test_generate_stability_report_with_criteria(self, temp_dir, sample_analyzer):
        """Test generating stability report with criteria results."""
        # Skip test - evaluate_stability_criteria not yet implemented
        pytest.skip("evaluate_stability_criteria function not yet implemented")
    
    def test_generate_complete_report(self, temp_dir, sample_hull, sample_cg, sample_analyzer):
        """Test generating complete analysis report."""
        curve = sample_analyzer.generate_stability_curve()
        metrics = sample_analyzer.analyze_stability()
        filepath = Path(temp_dir) / 'complete_report.md'
        
        generate_complete_report(sample_hull, sample_cg, curve, metrics, filepath)
        
        # Verify file exists
        assert filepath.exists()
        
        # Read and verify content
        with open(filepath, 'r') as f:
            content = f.read()
            assert '# Complete Kayak Analysis Report' in content
            assert 'Table of Contents' in content
            assert 'Hull Geometry' in content
            assert 'Hydrostatic Properties' in content
            assert 'Center of Gravity' in content
            assert 'Stability Analysis' in content
    
    def test_generate_report_with_metadata(self, temp_dir, sample_hull, sample_cg, sample_analyzer):
        """Test generating report with custom metadata."""
        curve = sample_analyzer.generate_stability_curve()
        metrics = sample_analyzer.analyze_stability()
        filepath = Path(temp_dir) / 'report_metadata.md'
        metadata = {
            'name': 'Test Kayak',
            'description': 'Example kayak for testing'
        }
        
        generate_complete_report(sample_hull, sample_cg, curve, metrics, filepath, metadata=metadata)
        
        # Read and verify metadata appears
        with open(filepath, 'r') as f:
            content = f.read()
            assert 'Test Kayak' in content
            assert 'Example kayak for testing' in content


class TestExportIntegration:
    """Integration tests for export functionality."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for test outputs."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    def test_complete_export_workflow(self, temp_dir):
        """Test complete workflow: load → analyze → export."""
        # Load hull
        hull = load_hull_from_json('data/sample_hull_simple.json')
        
        # Setup analysis
        cg = CenterOfGravity(lcg=2.5, vcg=-0.3, tcg=0.0, total_mass=100.0, num_components=1)
        analyzer = StabilityAnalyzer(hull, cg, waterline_z=-0.1)
        
        # Perform analysis
        curve = analyzer.generate_stability_curve(max_angle=60)
        metrics = analyzer.analyze_stability()
        cb = calculate_center_of_buoyancy(hull, waterline_z=-0.1)
        
        # Export everything
        output_dir = Path(temp_dir) / 'output'
        
        export_hydrostatic_properties(cb, output_dir / 'hydrostatics.csv')
        export_stability_curve(curve, output_dir / 'stability_curve.csv')
        export_stability_metrics(metrics, output_dir / 'metrics.csv')
        export_cg_summary(cg, output_dir / 'cg.csv')
        generate_complete_report(hull, cg, curve, metrics, output_dir / 'report.md')
        
        # Verify all files created
        assert (output_dir / 'hydrostatics.csv').exists()
        assert (output_dir / 'stability_curve.csv').exists()
        assert (output_dir / 'metrics.csv').exists()
        assert (output_dir / 'cg.csv').exists()
        assert (output_dir / 'report.md').exists()
    
    def test_export_waterline_comparison(self, temp_dir):
        """Test exporting multi-waterline comparison."""
        from src.stability import calculate_stability_at_multiple_waterlines
        
        hull = load_hull_from_json('data/sample_hull_simple.json')
        cg = CenterOfGravity(lcg=2.5, vcg=-0.3, tcg=0.0, total_mass=100.0, num_components=1)
        
        # Calculate at multiple waterlines
        waterlines = [-0.15, -0.1, -0.05]
        curves = calculate_stability_at_multiple_waterlines(
            hull, cg, waterlines
        )
        
        # Convert list to dict
        results = {wl: curve for wl, curve in zip(waterlines, curves)}
        
        filepath = Path(temp_dir) / 'waterline_comparison.csv'
        export_waterline_comparison(results, filepath)
        
        # Verify file exists
        assert filepath.exists()
        
        # Read and verify content
        with open(filepath, 'r') as f:
            reader = csv.reader(f)
            lines = list(reader)
            # Find data lines
            data_lines = [line for line in lines if not line[0].startswith('#') and line[0].replace('.', '').replace('-', '').isdigit()]
            
            # Should have one row per waterline
            assert len(data_lines) == len(waterlines)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

