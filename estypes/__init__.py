from __future__ import annotations

from typing import List, Literal, Optional, TypedDict


class MappingBuilder(dict):
    def properties(
        self,
        type: Literal[
            "binary",
            "boolean",
            "Keywords",
            "Numbers",
            "date",
            "date_nanos",
            "alias",
            "object",
            "flattened",
            "nested",
            "join",
            "long_range",
            "double_range",
            "date_range",
            "ip_range",
            "ip",
            "version",
            "murmur3",
            "aggregate_metric_double",
            "histogram",
            "text",
            "annotated-text",
            "completion",
            "search_as_you_type",
            "token_count",
            "dense_vector",
            "sparse_vector",
            "rank_feature",
            "rank_features",
            "geo_point",
            "geo_shape",
            "point",
            "shape",
            "percolator",
        ],
    ):
        self["type"] = type


class ESPropetry(TypedDict):
    name: Optional[str]
    type: Literal[
        "binary",
        "boolean",
        Literal["keyword", "constant_keyword", "wildcard"],  # keywords
        Literal[
            "long",
            "integer",
            "short",
            "byte",
            "double",
            "float",
            "half_float",
            "scaled_float",
            "unsigned_long",
        ],  # numbers
        Literal["date", "date_nanos"],  # dates
        "alias",
        "object",
        "flattened",
        "nested",
        "join",
        "long_range",
        "double_range",
        "date_range",
        "ip_range",
        "ip",
        "version",
        "murmur3",
        "aggregate_metric_double",
        "histogram",
        "text",
        "annotated-text",
        "completion",
        "search_as_you_type",
        "token_count",
        "dense_vector",
        "sparse_vector",
        "rank_feature",
        "rank_features",
        "geo_point",
        "geo_shape",
        "point",
        "shape",
        "percolator",
    ]
    fields: Optional["ESPropetry"]
