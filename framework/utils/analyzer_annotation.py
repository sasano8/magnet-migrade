from __future__ import annotations

from .analyzer_any import AnyAnalyzer
from .decorator import extensionmethod


class AnnotationAnalyzer(AnyAnalyzer):
    # __root__: アノテーションを意味するタイプなんてあるのか？

    @staticmethod
    def is_annotatable(self):
        pass
