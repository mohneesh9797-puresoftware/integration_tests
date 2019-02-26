# -*- coding: utf-8 -*-
import fauxfactory
import pytest

from cfme import test_requirements
from cfme.utils.appliance.implementations.ui import navigate_to
from cfme.utils.update import update

pytestmark = [test_requirements.automate]


@pytest.fixture(
    scope="module",
    params=["plain", "nested_existing"])
def parent_namespace(request, domain):
    if request.param == 'plain':
        return domain
    else:
        return domain.namespaces.create(
            name=fauxfactory.gen_alpha(),
            description=fauxfactory.gen_alpha()
        )


@pytest.mark.sauce
@pytest.mark.tier(1)
def test_namespace_crud(parent_namespace):
    """
    Polarion:
        assignee: ghubale
        casecomponent: Automate
        caseimportance: critical
        initialEstimate: 1/16h
        tags: automate
    """
    ns = parent_namespace.namespaces.create(
        name=fauxfactory.gen_alpha(),
        description=fauxfactory.gen_alpha())
    assert ns.exists
    updated_description = "editdescription{}".format(fauxfactory.gen_alpha())
    with update(ns):
        ns.description = updated_description
    assert ns.exists
    ns.delete(cancel=True)
    assert ns.exists
    ns.delete()
    assert not ns.exists


@pytest.mark.tier(1)
def test_namespace_delete_from_table(parent_namespace):
    """
    Polarion:
        assignee: ghubale
        casecomponent: Automate
        caseimportance: medium
        initialEstimate: 1/30h
        tags: automate
    """
    generated = []
    for _ in range(3):
        namespace = parent_namespace.namespaces.create(
            name=fauxfactory.gen_alpha(),
            description=fauxfactory.gen_alpha())
        generated.append(namespace)

    parent_namespace.namespaces.delete(*generated)
    for namespace in generated:
        assert not namespace.exists


@pytest.mark.tier(2)
def test_duplicate_namespace_disallowed(parent_namespace):
    """
    Polarion:
        assignee: ghubale
        casecomponent: Automate
        caseposneg: negative
        initialEstimate: 1/16h
        tags: automate
    """
    ns = parent_namespace.namespaces.create(
        name=fauxfactory.gen_alpha(),
        description=fauxfactory.gen_alpha())
    with pytest.raises(Exception, match="Name has already been taken"):
        parent_namespace.namespaces.create(
            name=ns.name,
            description=ns.description)


@pytest.mark.tier(2)
def test_wrong_namespace_name(domain):
    """To test whether namespace is creating with wrong name or not.
       wrong_namespace: 'Dummy Namespace' (This is invalid name of Namespace because there is space
       in the name)

    Polarion:
        assignee: ghubale
        casecomponent: Automate
        caseimportance: medium
        caseposneg: negative
        initialEstimate: 1/60h
        tags: automate
        testSteps:
            1. Navigate to Automation> Automate> Explorer
            2. Try to create namespace with name `Dummy Namespace` (I put space which is invalid)
        expectedResults:
            1.
            2. Should give proper flash message

    Bugzilla:
        1650071
    """
    wrong_namespace = 'Dummy Namespace'
    view = navigate_to(domain.namespaces, 'Add')
    view.name.fill(wrong_namespace)
    view.add_button.click()
    view.flash.assert_message('Name may contain only alphanumeric and _ . - $ characters')
    wrong_namespace = domain.namespaces.instantiate(name=wrong_namespace)
    assert not wrong_namespace.exists
