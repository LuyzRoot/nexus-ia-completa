# Plugins (NEXUS)

- Install plugin: POST /api/v1/admin/plugins/upload (zip file with plugin folder)
- List plugins: GET /api/v1/admin/plugins
- Enable: POST /api/v1/admin/plugins/{plugin_id}/enable
- Disable: POST /api/v1/admin/plugins/{plugin_id}/disable
- Remove: DELETE /api/v1/admin/plugins/{plugin_id}

Plugin contract:
- plugins/installed/<plugin_folder> should be a Python package importable as `plugins.installed.<plugin_folder>`.
- Provide `plugin.json` with metadata (id, name, version, description).
- Provide `setup(api)` function in package that registers skills/routers via provided PluginAPI.