#  This file is part of Pynguin.
#
#  SPDX-FileCopyrightText: 2019–2020 Pynguin Contributors
#
#  SPDX-License-Identifier: LGPL-3.0-or-later
#
import argparse
import importlib
import logging
from unittest import mock
from unittest.mock import MagicMock, call

import pytest

from pynguin.cli import (
    _create_argument_parser,
    _expand_arguments_if_necessary,
    _setup_logging,
    main,
)
from pynguin.generator import ReturnCode


def test_main_empty_argv():
    with mock.patch("pynguin.cli.Pynguin") as generator_mock:
        with mock.patch("pynguin.cli._create_argument_parser") as parser_mock:
            with mock.patch("pynguin.cli._setup_logging"):
                generator_mock.return_value.run.return_value = ReturnCode.OK
                parser = MagicMock()
                parser_mock.return_value = parser
                main()
                assert len(parser.parse_args.call_args[0][0]) > 0


def test_main_with_argv():
    with mock.patch("pynguin.cli.Pynguin") as generator_mock:
        with mock.patch("pynguin.cli._create_argument_parser") as parser_mock:
            with mock.patch("pynguin.cli._setup_logging"):
                generator_mock.return_value.run.return_value = ReturnCode.OK
                parser = MagicMock()
                parser_mock.return_value = parser
                args = ["foo", "--help"]
                main(args)
                assert parser.parse_args.call_args == call(args[1:])


def test__create_argument_parser():
    parser = _create_argument_parser()
    assert isinstance(parser, argparse.ArgumentParser)


def test__setup_logging_standard_with_log_file(tmp_path):
    logging.shutdown()
    importlib.reload(logging)
    _setup_logging(log_file=str(tmp_path / "pynguin-test.log"), verbosity=0)
    logger = logging.getLogger("")
    assert isinstance(logger, logging.Logger)
    assert logger.level == logging.DEBUG
    assert len(logger.handlers) == 2
    logging.shutdown()
    importlib.reload(logging)


def test__setup_logging_single_verbose_without_log_file():
    logging.shutdown()
    importlib.reload(logging)
    _setup_logging(1)
    logger = logging.getLogger("")
    assert len(logger.handlers) == 1
    assert logger.handlers[0].level == logging.INFO
    logging.shutdown()
    importlib.reload(logging)


def test__setup_logging_double_verbose_without_log_file():
    logging.shutdown()
    importlib.reload(logging)
    _setup_logging(2)
    logger = logging.getLogger("")
    assert len(logger.handlers) == 1
    assert logger.handlers[0].level == logging.DEBUG
    logging.shutdown()
    importlib.reload(logging)


def test__setup_logging_quiet_without_log_file():
    logging.shutdown()
    importlib.reload(logging)
    _setup_logging(-1)
    logger = logging.getLogger("")
    assert len(logger.handlers) == 1
    assert isinstance(logger.handlers[0], logging.NullHandler)
    logging.shutdown()
    importlib.reload(logging)


@pytest.mark.parametrize(
    "arguments, expected",
    [
        pytest.param(
            ["--foo", "bar", "--bar", "foo"], ["--foo", "bar", "--bar", "foo"]
        ),
        pytest.param(
            ["--foo", "bar", "--output_variables", "foo,bar,baz", "--bar", "foo"],
            ["--foo", "bar", "--output_variables", "foo", "bar", "baz", "--bar", "foo"],
        ),
        pytest.param(
            ["--foo", "bar", "--output_variables", "baz", "--bar", "foo"],
            ["--foo", "bar", "--output_variables", "baz", "--bar", "foo"],
        ),
    ],
)
def test__expand_arguments_if_necessary(arguments, expected):
    result = _expand_arguments_if_necessary(arguments)
    assert result == expected
