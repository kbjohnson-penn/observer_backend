from django.test import TestCase
from unittest.mock import MagicMock
from research.models import (
    VisitOccurrence, Person, Provider, Note, ConditionOccurrence,
    DrugExposure, ProcedureOccurrence, Measurement, Observation,
    PatientSurvey, ProviderSurvey, AuditLogs, Concept
)


class DatabaseRoutingTest(TestCase):
    """Test cases for research database routing."""
    
    def test_research_models_routing(self):
        """Test that research models are routed to research database."""
        from shared.db_router import DatabaseRouter
        
        router = DatabaseRouter()
        
        # Test reading from research database
        read_db = router.db_for_read(VisitOccurrence)
        self.assertEqual(read_db, 'research')
        
        # Test writing to research database
        write_db = router.db_for_write(VisitOccurrence)
        self.assertEqual(write_db, 'research')
        
        # Test other research models
        self.assertEqual(router.db_for_read(Person), 'research')
        self.assertEqual(router.db_for_read(Provider), 'research')
        self.assertEqual(router.db_for_read(Note), 'research')
        self.assertEqual(router.db_for_read(PatientSurvey), 'research')
        self.assertEqual(router.db_for_read(AuditLogs), 'research')
    
    def test_research_model_internal_relations(self):
        """Test that research models can relate to each other."""
        from shared.db_router import DatabaseRouter
        
        router = DatabaseRouter()
        
        # Create mock research objects
        research_obj1 = MagicMock()
        research_obj1._state.db = 'research'
        
        research_obj2 = MagicMock()
        research_obj2._state.db = 'research'
        
        # Should allow relations within research database
        result = router.allow_relation(research_obj1, research_obj2)
        self.assertTrue(result)
    
    def test_research_migration_routing(self):
        """Test migration routing for research models."""
        from shared.db_router import DatabaseRouter
        
        router = DatabaseRouter()
        
        # Should allow research app migrations on research database
        result = router.allow_migrate('research', 'research', 'VisitOccurrence')
        self.assertTrue(result)
        
        # Should not allow research app migrations on other databases
        result = router.allow_migrate('clinical', 'research', 'VisitOccurrence')
        self.assertFalse(result)
        
        result = router.allow_migrate('accounts', 'research', 'VisitOccurrence')
        self.assertFalse(result)