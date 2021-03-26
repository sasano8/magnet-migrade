import asyncio
import logging
from typing import Dict, Type

from .abc import Analyzer, BrokerImpl, TopicProvider

logger = logging.getLogger(__name__)


class BrokerRepository:
    __brokers__: Dict[str, Type[BrokerImpl]] = {}

    @classmethod
    def register(cls, broker: Type[BrokerImpl]):
        name = broker.get_name()
        if name in cls.__brokers__:
            raise Exception()

        cls.__brokers__[name] = broker
        return broker

    @classmethod
    def get(cls, broker_name: str):
        return cls.__brokers__[broker_name]

    @classmethod
    def get_names(cls):
        return [x for x in cls.__brokers__]


class TopicRepository:
    __topics__: Dict[str, Type[TopicProvider]] = {}

    @classmethod
    def register(cls, tp: Type[TopicProvider]):
        name = tp.get_name()
        if name in cls.__topics__:
            raise Exception(f"{tp} {name} is already registerd.")

        cls.__topics__[name] = tp
        return tp

    @classmethod
    def get(cls, topic_name: str):
        return cls.__topics__[topic_name]

    @classmethod
    def get_names(cls):
        return [x for x in cls.__topics__]


class AnalyzersRepository:
    __analyzers__: Dict[str, Type[Analyzer]] = {}

    @classmethod
    def register(cls, analyzer: Type[Analyzer]):
        name = analyzer.get_name()
        if name in cls.__analyzers__:
            raise Exception()

        cls.__analyzers__[name] = analyzer
        return analyzer

    @classmethod
    def get(cls, analyzer_name: str):
        return cls.__analyzers__[analyzer_name]

    @classmethod
    def get_names(cls):
        return [x for x in cls.__analyzers__]
