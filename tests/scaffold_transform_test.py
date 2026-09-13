"""Independent golden bytes and adversarial policy checks; no generated expected values."""
import importlib.util
from pathlib import Path
import tempfile
import unittest

spec=importlib.util.spec_from_file_location('transformer',Path(__file__).resolve().parents[1]/'scripts/scaffold-transform.py')
t=importlib.util.module_from_spec(spec); spec.loader.exec_module(t)

# Explicit source contract: expectations never call the production transformer.
SOURCE={
 'GoalStats.Template.sln': b'GoalStats.Template.Api',
 'src/GoalStats.Template.Api/GoalStats.Template.Api.csproj': b'<Project />',
 'src/GoalStats.Template.Api/Infrastructure/Database/TemplateDbContext.cs': b'class TemplateDbContext {}',
 'src/GoalStats.Template.Api/Infrastructure/Database/Migrations/TemplateDbContextModelSnapshot.cs': b'class TemplateDbContextModelSnapshot {}',
 'tests/GoalStats.Template.Api.UnitTests/GoalStats.Template.Api.UnitTests.csproj': b'GoalStats.Template.Api',
 'tests/GoalStats.Template.Api.IntegrationTests/GoalStats.Template.Api.IntegrationTests.csproj': b'GoalStats.Template.Api',
 'tests/GoalStats.Template.Api.IntegrationTests/Infrastructure/Database/TemplateDbContextTests.cs': b'class TemplateDbContextTests {}',
}
def payload(extra=None):
    return {p:('100644',v) for p,v in dict(SOURCE,**(extra or {})).items()}

class Transformer(unittest.TestCase):
    def test_valid_domains(self):
        for value in ['User','Match','Team','PlayerStats','Ab','A1','Abcdefghijklmno']:
            self.assertEqual(value,t.validate_domain(value))
    def test_invalid_domains(self):
        for value in ['','Template','user','USER','User-Service','User_Service','User.Service','../User','User$','User Service','Usér','U','Abcdefghijklmnop','User\n','$(shell echo User)','User\0']:
            with self.subTest(value=value),self.assertRaises(t.Refusal): t.validate_domain(value)
    def test_four_families(self):
        self.assertEqual(b'GoalStats.User.Api UserDbContext goalstats-user-api goalstats_user_local',t.transform(b'GoalStats.Template.Api TemplateDbContext goalstats-template-api goalstats_template_local','User'))
    def test_multiword_lowercase(self):
        self.assertEqual(b'goalstats-playerstats goalstats_playerstats',t.transform(b'goalstats-template goalstats_template','PlayerStats'))
    def test_context_suffixes(self):
        self.assertEqual(b'UserDbContext UserDbContextTests UserDbContextModelSnapshot',t.transform(b'TemplateDbContext TemplateDbContextTests TemplateDbContextModelSnapshot','User'))
    def test_unexpected_embeddings(self):
        for token in [b'XGoalStats.Template',b'GoalStats.TemplateMore',b'Other.GoalStats.Template',b'XTemplateDbContext',b'TemplateDbContextFactory',b'TemplateDbContextTestsExtra',b'Xgoalstats-template',b'prefix-goalstats-template',b'goalstats-templateExtra',b'xgoalstats_template',b'goalstats_templateExtra']:
            with self.subTest(token=token),self.assertRaises(t.Refusal): t.transform(token,'User')
    def test_generic_prose_urls_and_domain_unchanged(self):
        data=b'Template Service Api GoalStats Item Action ItemModel ActionModel ItemStatus ActionType /api/items /api/actions https://example.org/Template Version="9.0.1"'
        self.assertEqual(data,t.transform(data,'User'))
    def test_migration_metadata_and_operations(self):
        body=b'20260908043250_InitialCreate InitialCreate Up Down Items Actions Id constraints indexes relationships'
        self.assertEqual(b'namespace GoalStats.User.Api; typeof(UserDbContext); '+body,t.transform(b'namespace GoalStats.Template.Api; typeof(TemplateDbContext); '+body,'User'))
    def test_swagger(self):
        self.assertEqual(b'SwaggerEndpoint("v1/swagger.json", "GoalStats.User.Api v1")',t.transform(b'SwaggerEndpoint("v1/swagger.json", "GoalStats.Template.Api v1")','User'))
    def test_paths_and_anchors(self):
        output,mapping=t.plan(payload(),'User')
        self.assertEqual('GoalStats.User.sln',mapping['GoalStats.Template.sln'])
        self.assertIn('src/GoalStats.User.Api/Infrastructure/Database/UserDbContext.cs',output)
        self.assertIn('tests/GoalStats.User.Api.IntegrationTests/Infrastructure/Database/UserDbContextTests.cs',output)
        self.assertFalse(any(t.MATCH.search(p.encode()+v[1]) for p,v in output.items()))
    def test_migration_filename_preserved(self):
        name='src/GoalStats.Template.Api/Infrastructure/Database/Migrations/20260908043250_InitialCreate.cs'
        out,mapping=t.plan(payload({name:b'namespace GoalStats.Template.Api; Items Actions'}),'User')
        target='src/GoalStats.User.Api/Infrastructure/Database/Migrations/20260908043250_InitialCreate.cs'
        self.assertEqual(target,mapping[name]);self.assertEqual(b'namespace GoalStats.User.Api; Items Actions',out[target][1])
    def test_bom_crlf_no_final_newline_mode(self):
        data=payload();data['script.sh']=('100755',b'\xef\xbb\xbfGoalStats.Template.Api\r\nTemplate Service')
        out,_=t.plan(data,'User');self.assertEqual(('100755',b'\xef\xbb\xbfGoalStats.User.Api\r\nTemplate Service'),out['script.sh'])
    def test_invalid_text(self):
        for data in [b'\xff',b'x\0y']:
            with self.assertRaises(t.Refusal):t.plan(payload({'bad.md':data}),'User')
    def test_opaque_unchanged(self):
        out,_=t.plan(payload({'data.bin':b'\0\xffTemplate'}),'User');self.assertEqual(b'\0\xffTemplate',out['data.bin'][1])
    def test_opaque_token_refused(self):
        for token in t.TOKENS:
            with self.assertRaises(t.Refusal): t.plan(payload({'data.bin':b'\0'+token}),'User')
    def test_opaque_identity_path_refused(self):
        with self.assertRaises(t.Refusal):t.plan(payload({'GoalStats.Template.bin':b'abc'}),'User')
    def test_missing_anchors(self):
        for path in SOURCE:
            data=payload();del data[path]
            with self.assertRaises(t.Refusal): t.plan(data,'User')
    def test_zero_replacement_source(self):
        with self.assertRaises(t.Refusal):t.plan({'README.md':('100644',b'old generic template')},'User')
    def test_duplicate_transformed_paths(self):
        with self.assertRaises(t.Refusal):t.plan(payload({'GoalStats.User.sln':b'x'}),'User')
    def test_case_collisions(self):
        for paths in [['a.cs','A.cs'],['Dir/a.cs','dir/b.cs']]:
            with self.assertRaises(t.Refusal): t.collision_check(paths)
    def test_file_directory_conflict(self):
        for paths in [['a','a/b'],['a/b','a']]:
            with self.assertRaises(t.Refusal):t.collision_check(paths)
    def test_unsafe_paths(self):
        for path in ['../x','/x','a/./b','a//b','a\\b','name.','CON.cs','a/lpt1','a/.git/x','bad name','a/é','-bad','a'*256]:
            with self.subTest(path=path),self.assertRaises(t.Refusal):t.validate_path(path)
    def test_output_verification_detects_corruption(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory); (root/'a.md').write_bytes(b'bad')
            with self.assertRaises(t.Refusal):t.verify_output(root,{'a.md':('100644',b'good')})
    def test_residual_guard(self):
        with self.assertRaisesRegex(t.Refusal,'Residual'):
            t.transform(b'GoalStats.Template', 'Template')

    def test_source_manifest_rejects_changed_bytes(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);source=root/'source';source.mkdir();(source/'a.md').write_bytes(b'changed')
            manifest=root/'manifest';manifest.write_text('100644\t'+t.blob_hash(b'original')+'\ta.md\n')
            with self.assertRaises(t.Refusal):t.read_source(source,manifest)

if __name__=='__main__': unittest.main()
