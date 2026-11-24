import copy, unittest
from build import load, render, url

class ContentRenderingTests(unittest.TestCase):
    def test_current_content_renders(self):
        page=render(load())
        self.assertIn('Jake’s field notes',page)
        self.assertIn('PolyViz',page)
        self.assertIn('mailto:jseungjoonhwang66@gmail.com',page)

    def test_text_is_escaped_and_not_executed(self):
        data=load();data['about']['bio']='<script>alert("test")</script> $contact'
        page=render(data)
        self.assertNotIn('<script>alert',page)
        self.assertIn('&lt;script&gt;',page)
        self.assertIn('$contact',page)

    def test_unsafe_links_rejected(self):
        for value in ['javascript:alert(1)','data:text/html,test','//evil.test','../secret','https://test.test/\nfoo','\\evil.test']:
            with self.subTest(value=value), self.assertRaises(ValueError):url(value)

    def test_duplicate_project_anchor_rejected(self):
        data=load();data['projects']['items'].append(copy.deepcopy(data['projects']['items'][0]))
        with self.assertRaises(ValueError):render(data)

    def test_lists_can_be_added_and_removed(self):
        data=load();data['projects']['items']=[];data['experience']['items']=[]
        self.assertNotIn('id="polyviz"',render(data))
        data=load();project=copy.deepcopy(data['projects']['items'][0]);project['id']='new-project';project['name']='New work';data['projects']['items'].append(project)
        self.assertIn('id="new-project"',render(data))

if __name__=='__main__':unittest.main()
