import pytest

from ..models import PreflightResult
from ..serializers import (
    PreflightResultSerializer,
    JobSerializer,
)


@pytest.mark.django_db
class TestPreflightSerializer:
    def test_preflight_error_count(
            self, user_factory, plan_factory, preflight_result_factory):
        user = user_factory()
        plan = plan_factory()
        preflight = preflight_result_factory(
            user=user,
            organization_url=user.instance_url,
            plan=plan,
            results={
                0: [{'status': 'error'}],
            },
            status=PreflightResult.Status.complete,
        )
        serializer = PreflightResultSerializer(instance=preflight).data
        assert serializer["error_count"] == 1
        assert serializer["warning_count"] == 0

    def test_preflight_warning_count(
            self, user_factory, plan_factory, preflight_result_factory):
        user = user_factory()
        plan = plan_factory()
        preflight = preflight_result_factory(
            user=user,
            organization_url=user.instance_url,
            plan=plan,
            results={
                0: [{'status': 'warn'}],
            },
            status=PreflightResult.Status.complete,
        )
        serializer = PreflightResultSerializer(instance=preflight).data
        assert serializer["error_count"] == 0
        assert serializer["warning_count"] == 1

    def test_preflight_is_ready(
            self, user_factory, plan_factory, preflight_result_factory):
        user = user_factory()
        plan = plan_factory()
        preflight = preflight_result_factory(
            user=user,
            organization_url=user.instance_url,
            plan=plan,
            results={
                0: [{'status': 'warn'}],
            },
            status=PreflightResult.Status.complete,
        )
        serializer = PreflightResultSerializer(instance=preflight).data
        assert serializer["is_ready"]

    def test_preflight_is_not_ready(
            self, user_factory, plan_factory, preflight_result_factory):
        user = user_factory()
        plan = plan_factory()
        preflight = preflight_result_factory(
            user=user,
            organization_url=user.instance_url,
            plan=plan,
            results={
                0: [{'status': 'error'}],
            },
            status=PreflightResult.Status.complete,
        )
        serializer = PreflightResultSerializer(instance=preflight).data
        assert not serializer["is_ready"]


@pytest.mark.django_db
class TestJob:
    def test_create_good(
            self, rf, user_factory, plan_factory, step_factory,
            preflight_result_factory):
        plan = plan_factory()
        user = user_factory()
        step1 = step_factory(plan=plan)
        step2 = step_factory(plan=plan)
        step3 = step_factory(plan=plan)
        request = rf.get('/')
        request.user = user
        preflight_result_factory(
            plan=plan,
            user=user,
            status=PreflightResult.Status.complete,
            results={
                str(step2.id): [{'status': 'error', 'message': ''}],
            },
        )
        preflight_result_factory(
            plan=plan,
            user=user,
            status=PreflightResult.Status.complete,
            results={
                str(step1.id): [{'status': 'warn', 'message': ''}],
                str(step2.id): [{'status': 'skip', 'message': ''}],
                str(step3.id): [{'status': 'optional', 'message': ''}],
            },
        )
        data = {
            'plan': str(plan.id),
            'steps': [str(step1.id), str(step2.id), str(step3.id)],
        }
        serializer = JobSerializer(data=data, context=dict(request=request))

        assert serializer.is_valid(), serializer.errors

    def test_create_bad_preflight(
            self, rf, user_factory, plan_factory, step_factory,
            preflight_result_factory):
        plan = plan_factory()
        user = user_factory()
        step1 = step_factory(plan=plan)
        step2 = step_factory(plan=plan)
        step3 = step_factory(plan=plan)
        request = rf.get('/')
        request.user = user
        preflight_result_factory(
            plan=plan,
            user=user,
            status=PreflightResult.Status.complete,
            results={
                str(step2.id): [{'status': 'error', 'message': ''}],
            },
        )
        data = {
            'plan': str(plan.id),
            'steps': [str(step1.id), str(step2.id), str(step3.id)],
        }
        serializer = JobSerializer(data=data, context=dict(request=request))

        assert not serializer.is_valid(), serializer.errors

    def test_create_bad_no_preflight(self, rf, user_factory, plan_factory):
        plan = plan_factory()
        user = user_factory()
        request = rf.get('/')
        request.user = user
        data = {
            'plan': str(plan.id),
            'steps': [],
        }
        serializer = JobSerializer(data=data, context=dict(request=request))

        assert not serializer.is_valid(), serializer.errors

    def test_invalid_steps(
            self, rf, plan_factory, user_factory, step_factory,
            preflight_result_factory):
        plan = plan_factory()
        user = user_factory()
        step_factory(is_required=True, plan=plan)
        step2 = step_factory(is_required=False, plan=plan)

        request = rf.get('/')
        request.user = user
        preflight_result_factory(
            plan=plan,
            user=user,
            status=PreflightResult.Status.complete,
            results={},
        )
        data = {
            'plan': str(plan.id),
            'steps': [str(step2.id)],
        }
        serializer = JobSerializer(data=data, context=dict(request=request))

        assert not serializer.is_valid(), serializer.errors

    def test_invalid_steps_made_valid_by_preflight(
            self, rf, plan_factory, user_factory, step_factory,
            preflight_result_factory):
        plan = plan_factory()
        user = user_factory()
        step1 = step_factory(is_required=True, plan=plan)
        step2 = step_factory(is_required=False, plan=plan)

        request = rf.get('/')
        request.user = user
        preflight_result_factory(
            plan=plan,
            user=user,
            status=PreflightResult.Status.complete,
            results={
                str(step1.id): [{'status': 'optional', 'message': ''}],
            },
        )
        data = {
            'plan': str(plan.id),
            'steps': [str(step2.id)],
        }
        serializer = JobSerializer(data=data, context=dict(request=request))

        assert serializer.is_valid(), serializer.errors

    def test_no_context(self, job_factory):
        job = job_factory()
        serializer = JobSerializer(instance=job)

        assert serializer.data['org_name'] is None
        assert serializer.data['organization_url'] is None

    def test_patch(self, rf, job_factory, plan_factory, user_factory):
        plan = plan_factory()
        user = user_factory()
        request = rf.get('/')
        request.user = user
        job = job_factory(user=user, plan=plan)
        serializer = JobSerializer(
            job,
            data={'is_public': False},
            partial=True,
            context=dict(request=request),
        )

        assert serializer.is_valid(), serializer.errors
