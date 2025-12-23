"""
Forms for file upload and validation
"""

from django import forms
from django.core.exceptions import ValidationError
import pandas as pd
import numpy as np


class CSVUploadForm(forms.Form):
    """Form for uploading CSV files"""

    spine_file = forms.FileField(
        label='Spine CSV',
        required=True,
        help_text='Upload spine sensor CSV file (spine_dot.csv)'
    )

    pelvis_file = forms.FileField(
        label='Pelvis CSV',
        required=True,
        help_text='Upload pelvis sensor CSV file (pelvis_dot.csv)'
    )

    def clean_spine_file(self):
        """Validate spine CSV file"""
        return self._validate_csv_file(self.cleaned_data['spine_file'], 'spine')

    def clean_pelvis_file(self):
        """Validate pelvis CSV file"""
        return self._validate_csv_file(self.cleaned_data['pelvis_file'], 'pelvis')

    def _validate_csv_file(self, file, file_type):
        """
        Validate uploaded CSV file

        Args:
            file: Uploaded file
            file_type: 'spine' or 'pelvis'

        Returns:
            file: Validated file

        Raises:
            ValidationError: If validation fails
        """

        # Check file extension
        if not file.name.endswith('.csv'):
            raise ValidationError(
                f'Invalid file format. Please upload a CSV file. (E001)',
                code='invalid_extension'
            )

        # Check file size (max 50MB)
        max_size = 50 * 1024 * 1024  # 50MB in bytes
        if file.size > max_size:
            raise ValidationError(
                f'File too large. Maximum size is 50MB. (E002)',
                code='file_too_large'
            )

        # Try to read and validate CSV structure
        try:
            # Read first few lines to check structure
            file.seek(0)
            df = pd.read_csv(file, nrows=10)

            # Check required columns
            required_columns = ['SampleTimeFine', 'Quat_W', 'Quat_X', 'Quat_Y', 'Quat_Z']
            df.columns = df.columns.str.strip()
            missing_columns = [col for col in required_columns if col not in df.columns]

            if missing_columns:
                raise ValidationError(
                    f'Missing required columns: {", ".join(missing_columns)}. (E002)',
                    code='missing_columns'
                )

            # Reset file pointer
            file.seek(0)

            # Read full file to check minimum rows
            df_full = pd.read_csv(file)
            if len(df_full) < 100:
                raise ValidationError(
                    f'Insufficient data. Minimum 100 rows required, found {len(df_full)}. (E003)',
                    code='insufficient_data'
                )

            # Validate quaternion magnitudes (should be ≈ 1)
            quat_w = df_full['Quat_W'].values
            quat_x = df_full['Quat_X'].values
            quat_y = df_full['Quat_Y'].values
            quat_z = df_full['Quat_Z'].values

            quat_magnitude = np.sqrt(quat_w**2 + quat_x**2 + quat_y**2 + quat_z**2)

            # Check if quaternions are within acceptable range (0.9 to 1.1)
            invalid_quats = np.where((quat_magnitude < 0.9) | (quat_magnitude > 1.1))[0]
            if len(invalid_quats) > len(df_full) * 0.1:  # More than 10% invalid
                raise ValidationError(
                    f'Invalid quaternion data. {len(invalid_quats)} rows have quaternion magnitude outside acceptable range (0.9-1.1). (E005)',
                    code='invalid_quaternions'
                )

            # Reset file pointer for later use
            file.seek(0)

        except pd.errors.ParserError as e:
            raise ValidationError(
                f'Failed to parse CSV file: {str(e)} (E004)',
                code='parse_error'
            )
        except ValidationError:
            # Re-raise validation errors
            raise
        except Exception as e:
            raise ValidationError(
                f'Error reading CSV file: {str(e)} (E004)',
                code='read_error'
            )

        return file
