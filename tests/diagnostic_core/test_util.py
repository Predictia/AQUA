import pytest
import argparse
from aqua.diagnostics.core import template_parse_arguments, open_cluster, close_cluster

loglevel = 'DEBUG'


@pytest.mark.aqua
def test_template_parse_arguments():
    """Test the template_parse_arguments function"""
    parser = argparse.ArgumentParser()
    parser = template_parse_arguments(parser)
    args = parser.parse_args(["--loglevel", "DEBUG", "--catalog", "test_catalog", "--model", "test_model"])

    assert args.loglevel == "DEBUG"
    assert args.catalog == "test_catalog"
    assert args.model == "test_model"
    assert args.exp is None
    assert args.source is None
    assert args.config is None

@pytest.mark.aqua
def test_cluster():
    """Test the cluster functions"""
    client, cluster, private_cluster = open_cluster(None, None, loglevel)

    assert client is None
    assert cluster is None
    assert private_cluster is False

    client, cluster, private_cluster = open_cluster(2, None, loglevel)

    assert client is not None
    assert cluster is not None
    assert private_cluster is True

    # Use the cluster generated in the previous test as an input to the next test

    previous_cluster = cluster
    client, cluster, private_cluster = open_cluster(2, cluster, loglevel)

    assert client is not None
    assert cluster is previous_cluster
    assert private_cluster is False

    close_cluster(client, cluster, private_cluster)
