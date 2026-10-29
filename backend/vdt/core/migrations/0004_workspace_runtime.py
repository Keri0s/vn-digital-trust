"""Additive snapshot binding; no runtime grants or existing row rewrites.

Downgrade refuses to discard any binding created through the new feature.
"""
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [('core','0003_access_runtime')]
    operations = [migrations.RunSQL('''
        ALTER TABLE vdt.assessment_scenario ADD COLUMN scenario_snapshot_id uuid REFERENCES vdt.scenario_snapshot;
        CREATE FUNCTION vdt.stamp_workspace_snapshot() RETURNS trigger LANGUAGE plpgsql AS $$
        BEGIN
          IF NEW.api_payload_schema_version='workspace-v0.1' THEN
            NEW.api_payload := jsonb_set(NEW.api_payload,'{created_at}',to_jsonb(NEW.created_at));
          END IF;
          RETURN NEW;
        END $$;
        CREATE TRIGGER zz_workspace_snapshot_metadata BEFORE INSERT ON vdt.snapshot_registry
          FOR EACH ROW EXECUTE FUNCTION vdt.stamp_workspace_snapshot();
    ''', reverse_sql='''
        DO $$ BEGIN
          IF EXISTS(SELECT 1 FROM vdt.assessment_scenario WHERE scenario_snapshot_id IS NOT NULL)
             OR EXISTS(SELECT 1 FROM vdt.snapshot_registry WHERE api_payload_schema_version='workspace-v0.1') THEN
            RAISE EXCEPTION 'Cannot downgrade while workspace snapshots or bindings exist';
          END IF;
        END $$;
        DROP TRIGGER zz_workspace_snapshot_metadata ON vdt.snapshot_registry;
        DROP FUNCTION vdt.stamp_workspace_snapshot();
        ALTER TABLE vdt.assessment_scenario DROP COLUMN scenario_snapshot_id;
    ''')]
