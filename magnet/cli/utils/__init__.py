def get_module_and_attr(target_module_attr):
    from importlib import import_module

    module, attr = target_module_attr.split(":")
    module = import_module(module)
    app = getattr(module, attr)

    # TODO: app.run のインターフェース確認

    return (module, app)
