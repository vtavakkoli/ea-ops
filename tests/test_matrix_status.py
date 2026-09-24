"""Matrix download status must not turn a successful load into a failed gate."""
import unittest
from unittest.mock import patch
from eaops.archimate_matrix import RelationshipMatrixError
from eaops.core import RepositoryModel, validate


class MatrixStatusTests(unittest.TestCase):
    def repository(self):
        from pathlib import Path
        return RepositoryModel(root=Path('.'), config={}, metamodel={
            'relationshipMatrix': {'version': '3.2', 'required': True}
        })

    def test_loaded_version_is_not_an_error(self):
        with patch('eaops.core.load_relationship_matrix', return_value=('3.2', {})):
            self.assertNotIn('RELATIONSHIP_MATRIX_UNAVAILABLE', [i.code for i in validate(self.repository())])

    def test_download_failure_still_blocks_validation(self):
        with patch('eaops.core.load_relationship_matrix', side_effect=RelationshipMatrixError('download failed')):
            issues = validate(self.repository())
            issue = next(i for i in issues if i.code == 'RELATIONSHIP_MATRIX_UNAVAILABLE')
            self.assertEqual(('error', 'download failed'), (issue.severity, issue.message))
