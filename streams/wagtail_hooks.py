"""Richtext hooks."""
import wagtail.admin.rich_text.editors.draftail.features as draftail_features
from wagtail.admin.rich_text.converters.html_to_contentstate import InlineStyleElementHandler
from wagtail.core import hooks


@hooks.register("register_rich_text_features")
def register_centertext_feature(features):
	"""Adds blockquote / pullquote to richtext editor."""

	# Step 1
	feature_name = "blockquote"
	type_ = "BLOCKQUOTE"
	tag = "blockquote"

	# Step 2
	control = {
		"type": type_,
		"label": "❝",
		"description": "Block Quote",
		"element": "blockquote",
	}

	# Step 3
	features.register_editor_plugin(
		"draftail", feature_name, draftail_features.InlineStyleFeature(control)
	)

	# Step 4
	db_conversion = {
		"from_database_format": {tag: InlineStyleElementHandler(type_)},
		"to_database_format": {
			"style_map": {
				type_: {
					"element": tag,
					"props": {
						"class": "pullout"
					}
				}
			}
		}
	}

	# Step 5
	features.register_converter_rule("contentstate", feature_name, db_conversion)

	# Step 6, This is optional.
	features.default_features.append(feature_name)
