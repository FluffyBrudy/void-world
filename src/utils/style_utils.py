from ttypes.index_type import BoxModel, BoxModelResult


def set_box_model_defaults(model: BoxModel) -> BoxModel:
    return {
        "width": model.get("width", 0),
        "height": model.get("height", 0),
        "padding_x": model.get("padding_x", 0),
        "padding_y": model.get("padding_y", 0),
        "border_width": model.get("border_width", 0),
        "margin_x": model.get("margin_x", 0),
        "margin_y": model.get("margin_y", 0),
    }


def generate_box_model(model: BoxModel) -> BoxModelResult:
    assert isinstance(model, dict)

    model = set_box_model_defaults(model)

    for value in model.values():
        assert isinstance(value, int) and value >= 0

    inner_x = 2 * (model["padding_x"] + model["border_width"])
    inner_y = 2 * (model["padding_y"] + model["border_width"])

    return {
        "left": model["padding_x"] + model["border_width"],
        "top": model["padding_y"] + model["border_width"],
        "offset_x": model["margin_x"],
        "offset_y": model["margin_y"],
        "full_width": model["width"],
        "full_height": model["height"],
        "content_width": model["width"] - inner_x,
        "content_height": model["height"] - inner_y,
    }
