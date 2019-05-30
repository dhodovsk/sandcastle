# MIT License
#
# Copyright (c) 2018-2019 Red Hat, Inc.

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
import pytest
from flexmock import flexmock

from kubernetes.client.rest import ApiException
from generator.deploy_openshift_pod import OpenshiftDeployer
from generator.exceptions import GeneratorDeployException


@pytest.fixture()
def pod_not_deployed():
    return {
            "kind": "Status",
            "apiVersion": "v1",
            "metadata": {},
            "status": "Failure",
            "message": "pods \"generator\" not found",
            "reason": "NotFound",
            "details": {
                "name": "generator",
                "kind": "pods"
            },
            "code": 404
        }


@pytest.fixture()
def pod_json_deployed():
    return {
        "kind": "Pod",
        "apiVersion": "v1",
        "metadata": {
            "name": "generator-5-qh85r",
            "generateName": "generator-5-",
            "namespace": "PROJECT_NAME",
            "selfLink": "/api/v1/namespaces/PROJECT_NAME/pods/generator-5-qh85r",
            "uid": "6d5ad24a-81d6-11e9-a2fa-fa163ed2928c",
            "resourceVersion": "488154842",
            "creationTimestamp": "2019-05-29T05:55:56Z",
            "labels": {
                "deployment": "generator-5",
                "deploymentconfig": "generator",
                "io.openshift.tags": "generator"
            },
            "annotations": {
                "openshift.io/deployment-config.latest-version": "5",
                "openshift.io/deployment-config.name": "generator",
                "openshift.io/deployment.name": "generator-5",
                "openshift.io/scc": "restricted"
            },
            "ownerReferences": [
                {
                    "apiVersion": "v1",
                    "kind": "ReplicationController",
                    "name": "generator-5",
                    "uid": "f4204b91-5c38-11e9-ac31-fa163ed2928c",
                    "controller": "true",
                    "blockOwnerDeletion": "true"
                }
            ]
        },
        "spec": {
            "volumes": [
                {
                    "name": "packit-generator",
                    "persistentVolumeClaim": {
                        "claimName": "claim.generator"
                    }
                },
            ],
            "containers": [
                {
                    "name": "generator",
                    "image": "docker.io/usercont/generator",
                    "env": [
                        {
                            "name": "NAMESPACE",
                            "valueFrom": {
                                "configMapKeyRef": {
                                    "name": "common",
                                    "key": "project"
                                }
                            }
                        },
                    ],
                    "resources": {
                        "limits": {
                            "cpu": "400m",
                            "memory": "800Mi"
                        },
                        "requests": {
                            "cpu": "200m",
                            "memory": "400Mi"
                        }
                    },
                    "volumeMounts": [
                        {
                            "name": "packit-generator",
                            "mountPath": "/tmp/packit-generator"
                        },
                    ],
                    "terminationMessagePath": "/dev/termination-log",
                    "terminationMessagePolicy": "File",
                    "imagePullPolicy": "Always",
                }
            ],
            "restartPolicy": "Always",
            "terminationGracePeriodSeconds": 30,
            "dnsPolicy": "ClusterFirst",
            "nodeSelector": {
                "region": "compute"
            },
            "serviceAccountName": "generator",
            "serviceAccount": "generator",
            "imagePullSecrets": [
                {
                    "name": "generator-dockercfg-4bqcm"
                }
            ],
            "schedulerName": "default-scheduler",
            "tolerations": [
                {
                    "key": "node.kubernetes.io/memory-pressure",
                    "operator": "Exists",
                    "effect": "NoSchedule"
                }
            ]
        },
        "status": {
            "phase": "Running",
            "startTime": "2019-05-29T05:55:56Z",
            "containerStatuses": [
                {
                    "name": "generator",
                    "state": {
                        "running": {
                            "startedAt": "2019-05-29T05:56:29Z"
                        }
                    },
                    "lastState": {},
                    "ready": "true",
                    "restartCount": 0,
                    "image": "docker.io/usercont/generator:latest",
                    "imageID": "docker-pullable://docker.io/usercont/generator@sha256:51289119edf387c47ed149eb3382c23f4115bc343adcaaa6e1731d269b6ec70a",
                    "containerID": "docker://201ad777bb6d36077590fed8796bcd6170a62833c124467a1ffa2af4c60f1272"
                }
            ],
            "qosClass": "Burstable"
        }
    }


@pytest.fixture()
def pod_already_deployed(pod_json_deployed):
    raise ApiException(status=200, reason="Already exists")


@pytest.fixture()
def create_pod():
    return {

    }


@pytest.fixture()
def delete_pod():
    return {

    }


def test_is_pod_already_deployed():
    od = OpenshiftDeployer("/tmp", "cyborg", "bot-ferdinand")
    flexmock(od)\
        .should_receive("get_response_from_pod")\
        .and_raise(ApiException(status=200,
                                reason="POD already exists"))
    with pytest.raises(GeneratorDeployException):
        od.is_pod_already_deployed()


def test_pod_not_deployed(pod_not_deployed):
    od = OpenshiftDeployer("/tmp", "packit", "generator")
    flexmock(od).should_receive("get_response_from_pod").and_return(pod_not_deployed)
    assert od.is_pod_already_deployed()