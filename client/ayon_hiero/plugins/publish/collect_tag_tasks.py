from pyblish import api
from ayon_core.settings import get_current_project_settings
import json


DEFAULT_TASKS = ["compositing"]
class CollectClipTagTasks(api.InstancePlugin):
    """Collect Tags from selected track items."""

    order = api.CollectorOrder - 0.077
    label = "Collect Tag Tasks"
    hosts = ["hiero"]
    families = ["shot"]

    def process(self, instance):
        # gets tags
        tags = instance.data["tags"]

        instance.data["tasks"] = {}
        for tag in tags:
            t_metadata = dict(tag.metadata())
            if t_metadata.get("tag.json_metadata"):
                metadata = json.loads(t_metadata["tag.json_metadata"])
                product_type = metadata.get("productType")
                if product_type == "task":
                    task_type = metadata.get("type")
                    task_name = t_metadata.get("tag.label", "")
                    instance.data["tasks"][task_name] = {"type": task_type}
            else:
                # backward compatiblity for older tags
                t_product_type = t_metadata.get("tag.productType")
                if t_product_type is None:
                    t_product_type = t_metadata.get("tag.family", "")

                # gets only task product type tags and collect labels
                if "task" in t_product_type:
                    t_task_name = t_metadata.get("tag.label", "")
                    t_task_type = t_metadata.get("tag.type", "")
                    instance.data["tasks"][t_task_name] = {"type": t_task_type}
        self.log.debug(f"collected tasks:: {instance.data['tasks']}")
        
        for task in self.get_default_tasks():
            instance.data["tasks"].update({
                task: {"type": task.capitalize()}
            })

        self.log.info("Collected Tasks from Tags: `{}`".format(
            instance.data["tasks"]))

    def get_default_tasks(self):
        settings = get_current_project_settings()
        core_settings = settings["core"]
        for filter in core_settings.get("filter_env_profiles", []):
            if "default_conform_tasks" in filter.get("host_names", []):
                return filter.get("task_names", []) or DEFAULT_TASKS
                    
        return DEFAULT_TASKS