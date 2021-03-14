from inflector import Inflector


def test_infector():

    i = Inflector()

    result = i.camelize("trade_clients")
    assert result == "TradeClients"

    result = i.underscore("TradeClients")
    assert result == "trade_clients"

    result = i.titleize("HappyBirthDay")
    assert result == "Happy Birth Day"

    result = i.titleize("HappyBirthDay", "first")
    assert result == "Happy birth day"

    result = i.humanize("happy_birth_day")
    assert result == "Happy Birth Day"

    # 単数形を複数形にする
    result = i.pluralize("parameter")
    assert result == "parameters"

    # 複数形を単数形にする
    result = i.singularize("properties")
    assert result == "property"
