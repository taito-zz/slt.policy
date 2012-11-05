from Products.CMFCore.utils import getToolByName
from slt.policy.tests.base import IntegrationTestCase


class TestCase(IntegrationTestCase):
    """TestCase for upgrade steps."""

    def setUp(self):
        self.portal = self.layer['portal']

    def test_update_rolemap(self):
        permission = "slt.theme: Manage feed for shop top"
        self.portal.manage_acquiredPermissions()
        self.portal.manage_permission(permission)
        self.assertEqual(self.portal.acquiredRolesAreUsedBy(permission), '')
        roles = [item['name'] for item in self.portal.rolesOfPermission(
            permission) if item['selected'] == 'SELECTED']
        self.assertEqual(len(roles), 0)

        from slt.policy.upgrades import update_rolemap
        update_rolemap(self.portal)

        self.assertEqual(self.portal.acquiredRolesAreUsedBy(permission), 'CHECKED')
        roles = [item['name'] for item in self.portal.rolesOfPermission(
            permission) if item['selected'] == 'SELECTED']
        roles.sort()
        self.assertEqual(roles, [
            'Contributor',
            'Editor',
            'Manager',
            'Site Administrator'])

    def test_update_typeinfo(self):
        types = getToolByName(self.portal, 'portal_types')
        ctype = types.getTypeInfo('collective.cart.shopping.SubArticle')
        ctype.global_allow = True
        self.assertTrue(ctype.global_allow)

        from slt.policy.upgrades import update_typeinfo
        update_typeinfo(self.portal)

        self.assertFalse(ctype.global_allow)

    def test_update_registry(self):
        from zope.component import getUtility
        from plone.registry.interfaces import IRegistry
        record = getUtility(IRegistry).records.get('hexagonit.socialbutton.codes')
        record.value = {
            u'twitter': {u'code_text': u'<CODE />'},
        }

        self.assertEqual(getUtility(IRegistry)['hexagonit.socialbutton.codes'],
            {u'twitter': {u'code_text': u'<CODE />'}})

        from slt.policy.upgrades import update_registry
        update_registry(self.portal)

        self.assertEqual(getUtility(IRegistry)['hexagonit.socialbutton.codes'], {
            u'twitter': {u'code_text': u'<a class="social-button twitter" title="Twitter" href="https://twitter.com/share?text=${title}?url=${url}">\n<img src="${portal_url}/++resource++hexagonit.socialbutton/twitter.gif" />\n</a>'},
            u'facebook': {u'code_text': u'<a class="social-button facebook" title="Facebook" target="_blank" href="http://www.facebook.com/sharer.php?t=${title}&u=${url}">\n<img src="${portal_url}/++resource++hexagonit.socialbutton/facebook.gif" />\n</a>'},
            u'google-plus': {u'code_text': u'<a class="social-button googleplus" title="Google+" href="https://plusone.google.com/_/+1/confirm?hl=${lang}&title=${title}&url=${url}">\n<img src="${portal_url}/++resource++hexagonit.socialbutton/google-plus.gif" />\n</a>'},
        })