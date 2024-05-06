odoo.define('button_near_create.kanban_button', function(require) {
   "use strict";
   var KanbanController = require('web.KanbanController');
   var KanbanView = require('web.KanbanView');
   var viewRegistry = require('web.view_registry');
   var KanbanButton = KanbanController.include({
       buttons_template: 'button_near_create.button',
       events: _.extend({}, KanbanController.prototype.events, {
           'click .edit_project_action_kanban': '_EditProjectKanban',
       }),
       _EditProjectKanban: function () {
       var projectId = this.initialState.context.active_id

       var self = this;
        this.do_action({
           type: 'ir.actions.act_window',
           res_model: 'project.project',
           name :'Open Wizard',
           view_mode: 'form',
           view_type: 'form',
           views: [[false, 'form']],
           res_id: projectId,
           target: 'current',
       });
   }
   });
   var ProjectTaskKanbanView = KanbanView.extend({
       config: _.extend({}, KanbanView.prototype.config, {
           Controller: KanbanButton
       }),
   });
   viewRegistry.add('button_in_kanban', ProjectTaskKanbanView);
});

