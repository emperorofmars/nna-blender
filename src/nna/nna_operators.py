import bpy
from . import nna_tree_utils
from . import nna_json_utils


class InitializeNNAOperator(bpy.types.Operator):
	bl_idname = "nna.init"
	bl_label = "Initializie NNA"
	bl_options = {"REGISTER", "UNDO"}

	nna_init_collection: bpy.props.StringProperty(name = "nna_init_collection") # type: ignore
	
	def execute(self, context):
		if bpy.context.scene.collection.name == self.nna_init_collection:
			nna_tree_utils.init_nna_root(bpy.context.scene.collection)
			self.report({"INFO"}, "NNA inited in Scene Collection")
			return {"FINISHED"}
		else:
			for collection in [bpy.context.scene.collection, *bpy.context.scene.collection.children_recursive]:
				if(collection.name == self.nna_init_collection):
					nna_tree_utils.init_nna_root(collection)
					self.report({"INFO"}, "NNA inited in " + collection.name)
					return {"FINISHED"}
		return {"CANCELLED"}


class CreateNNATargetingObjectOperator(bpy.types.Operator):
	bl_idname = "nna.create_targeting_object"
	bl_label = "Initializie NNA for this Object"
	bl_options = {"REGISTER", "UNDO"}

	target_id: bpy.props.StringProperty(name = "target_id") # type: ignore
	
	def execute(self, context):
		nna_tree_utils.create_targeting_object(nna_tree_utils.find_nna_root(), self.target_id)
		self.report({"INFO"}, "Targeting object created")
		return {"FINISHED"}


class RemoveNNATargetingObjectOperator(bpy.types.Operator):
	bl_idname = "nna.remove_targeting_object"
	bl_label = "Remove NNA from this Object"
	bl_options = {"REGISTER", "UNDO"}

	target_id: bpy.props.StringProperty(name = "target_id") # type: ignore

	def invoke(self, context, event):
		return context.window_manager.invoke_confirm(self, event)
	
	def execute(self, context):
		nna_json_utils.remove_targeting_object(nna_tree_utils.find_nna_targeting_object(self.target_id))
		self.report({"INFO"}, "NNA functionality has been removed from: " + self.target_id)
		return {"FINISHED"}


class EditNNARawJsonOperator(bpy.types.Operator):
	bl_idname = "nna.edit_raw_json"
	bl_label = "Edit Raw NNA Json Object"
	bl_options = {"REGISTER", "UNDO"}

	target_id: bpy.props.StringProperty(name = "target_id") # type: ignore
	
	def invoke(self, context, event):
		return context.window_manager.invoke_props_dialog(self)
		
	def execute(self, context):
		try:
			nna_json = nna_json_utils.get_json_from_targetname(self.target_id)
			nna_json_utils.serialize_json_to_targetname(self.target_id, nna_json)
			self.report({'INFO'}, "Object Json successfully edited")
			return {"FINISHED"}
		except ValueError as error:
			self.report({'ERROR'}, str(error))
			return {"CANCELLED"}
	
	def draw(self, context):
		self.layout.label(text="Target Object: " + self.target)
		self.layout.prop(self, "json", text="", expand=True)


class AddNNARawJsonComponentOperator(bpy.types.Operator):
	bl_idname = "nna.add_raw_json_component"
	bl_label = "Add Raw Json Component"
	bl_options = {"REGISTER", "UNDO"}
	
	target_id: bpy.props.StringProperty(name = "targetId") # type: ignore

	new_component: bpy.props.StringProperty(name = "new_component") # type: ignore

	def invoke(self, context, event):
		return context.window_manager.invoke_props_dialog(self)
		
	def execute(self, context):
		try:
			nna_json = nna_json_utils.get_json_from_targetname(self.target_id)
			new_nna_json = nna_json_utils.add_component_to_nna(nna_json, self.new_component)
			nna_json_utils.serialize_json_to_targetname(self.target_id, new_nna_json)
			self.report({'INFO'}, "Component successfully added")
			return {"FINISHED"}
		except ValueError as error:
			self.report({'ERROR'}, str(error))
			return {"CANCELLED"}
	
	def draw(self, context):
		self.layout.label(text="Target Object: " + self.target_id)
		self.layout.prop(self, "new_component", text="", expand=True)


class EditNNARawJsonComponentOperator(bpy.types.Operator):
	bl_idname = "nna.edit_raw_json_component"
	bl_label = "Edit Raw Json Component"
	bl_options = {"REGISTER", "UNDO"}

	component_index: bpy.props.IntProperty(name = "component_index", default=-1) # type: ignore
	target_id: bpy.props.StringProperty(name = "target_id") # type: ignore

	json_component: bpy.props.StringProperty(name = "json_component") # type: ignore
	
	def invoke(self, context, event):
		nna_json = nna_json_utils.get_json_from_targetname(self.target_id)
		try:
			self.json_component = nna_json_utils.get_component_from_nna(nna_json, self.component_index)
		except ValueError as error:
			self.report({'ERROR'}, str(error))
			return None
		return context.window_manager.invoke_props_dialog(self)
		
	def execute(self, context):
		try:
			nna_json = nna_json_utils.get_json_from_targetname(self.target_id)
			jsonText = nna_json_utils.replace_component_in_nna(nna_json, self.json_component, self.component_index)
			nna_json_utils.serialize_json_to_targetname(self.target_id, jsonText)

			self.report({'INFO'}, "Component successfully edited")
			return {"FINISHED"}
		except ValueError as error:
			self.report({'ERROR'}, str(error))
			return {"CANCELLED"}
	
	def draw(self, context):
		self.layout.label(text="Target Object: " + self.target)
		self.layout.prop(self, "json_component", text="{\"t\":\"example\"}", expand=True)


class RemoveNNAJsonComponentOperator(bpy.types.Operator):
	bl_idname = "nna.remove_json_component"
	bl_label = "Remove Json Component"
	bl_options = {"REGISTER", "UNDO"}

	target_id: bpy.props.StringProperty(name = "target_id") # type: ignore
	component_index: bpy.props.IntProperty(name = "component_index", default=-1) # type: ignore

	def invoke(self, context, event):
		return context.window_manager.invoke_confirm(self, event)
	
	def execute(self, context):
		try:
			nna_json = nna_json_utils.get_json_from_targetname(self.target_id)
			jsonText = nna_json_utils.remove_component_from_nna(nna_json, self.component_index)
			nna_json_utils.serialize_json_to_targetname(self.target_id, jsonText)
			self.report({'INFO'}, "Component successfully removed")
			return {"FINISHED"}
		except ValueError as error:
			self.report({'ERROR'}, str(error))
			return {"CANCELLED"}
