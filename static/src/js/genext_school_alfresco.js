odoo.define('genext_school_alfresco.genext_school_alfresco.js', function(require){
    "use strict";
    var core = require('web.core');
    var common = require('web.form_common');
    var formats = require('web.formats');
    var FieldChar = core.form_widget_registry.get('char');
    var FieldBinaryFile = core.form_widget_registry.get('binary');
    
    var Widget = require('web.Widget');
    var Model = require('web.Model');
    var Data = require('web.data');
    var Dialog = require('web.Dialog');
    var NotificationManager = require('web.notification').NotificationManager;

    var SchoolFieldBinaryFile = common.AbstractField.extend(common.ReinitializeFieldMixin, {
        template: 'SchoolFieldBinaryFile', 
        init: function(field_manager, node) {
            alert('field_manager :'+field_manager);
            alert('node : '+node);
            var self = this;
            this._super(field_manager, node);
            this.binary_value = false;
            this.useFileAPI = !!window.FileReader;
            this.max_upload_size = 25 * 1024 * 1024; // 25Mo
            alert('init');
            if (!this.useFileAPI) {
                this.fileupload_id = _.uniqueId('o_fileupload');
                $(window).on(this.fileupload_id, function() {
                    var args = [].slice.call(arguments).slice(1);
                    self.on_file_uploaded.apply(self, args);
                });
            }
        },
        initialize_content: function() {
            alert('initialize_content');
            var self = this;
        
            
        },
        render_value: function() {
            alert('render value call');
        },
        store_dom_value: function(){
            this.internal_set_value(this.$input.val());
        },

        

        on_file_change: function(e) {
            alert('on_file_change');
            this.set_value("hello there");
            
        },
        stop: function() {
            alert('stop call');
            if (!this.useFileAPI) {
                $(window).off(this.fileupload_id);
            }
            this._super.apply(this, arguments);
        },
    });


    var ConfirmWidget = Widget.extend({
        events: {
            'click button.ok_button': function () {
                this.trigger('user_chose', true);
            },
            'click button.cancel_button': function () {
                this.trigger('user_chose', false);
            }
        },
        start: function() {
            this.$el.append("<div>Are you sure you want to perform this action?</div>" +
                "<button class='ok_button'>Ok</button>" +
                "<button class='cancel_button'>Cancel</button>");
        },
    });

    core.form_widget_registry.add('ConfirmWidget', ConfirmWidget);


    var CmisCreateFolderDialog = Dialog.extend({
         template: 'CmisCreateFolderDialog',
         init: function(parent, parent_cmisobject) {
             var self = this;
             var options = {
                 buttons: [
                     {text: _t("Create"),
                      classes: "btn-primary",
                      click: function () {
                          if(self.check_validity()){
                              self.on_click_create();
                          }
                      }
                     },
                     {text: _t("Close"),
                      click: function () { self.$el.parents('.modal').modal('hide');}},
                 ],
                 close: function () { self.close();}
             };
             this._super(parent, options);
             this.parent_cmisobject = parent_cmisobject;
             this.set_title(_t("Create Folder "));
         },

         on_click_create: function() {
             var self = this;
             var input = this.$el.find("input[type='text']")[0];
             framework.blockUI();
             var cmis_session = this.getParent().cmis_session;
             cmis_session
                 .createFolder(this.parent_cmisobject.objectId, input.value)
                 .ok(function(new_cmisobject) {
                     framework.unblockUI();
                     self.getParent().trigger('cmis_node_created', [new_cmisobject]);
                     self.$el.parents('.modal').modal('hide');
                  });
         },
         
         close: function() {
             this._super();
         }
    });



    var UploadField = common.AbstractField.extend(common.ReinitializeFieldMixin, {
        template: 'UploadField',
        events: {
            'change': 'store_dom_value',
        },
        init: function (field_manager, node) {
            console.log('Char init');
            this._super(field_manager, node);
            this.reader = new FileReader();
        },
        user_chose: function(confirm) {
            if (confirm) {
                console.log("The user agreed to continue");
            } else {
                console.log("The user refused to continue");
            }
        },
        initialize_content: function() {
            this.notification_manager = new NotificationManager(this);
            this.notification_manager.appendTo(this.$el);
            this.notification_manager.notify('SBS', 'whatever', true);
            console.log('this ',this);
            console.log('view ',this.view);
            console.log('dataset ',this.view.dataset);
            console.log('datarecord ',this.view.datarecord);
            console.log('dataset.model ',this.view.dataset.model);
            console.log('datarecord.id ',this.view.datarecord.id);
            this.view.dataset.write(this.view.datarecord.id, {name:'new Value',test_field:'hahaha'});
            console.log('Char initialize_content');
            var self = this;
            this.$input = this.$el;
            //self.$('.select_file_button').hide();
            this.$('.select_file_button').click(this.on_click);
            this.$('#easy-tree').jstree({
                "plugins" : ["contextmenu","dnd","unique","checkbox"],
                'core' : {
                    "check_callback" : true,
                    'data' :[
                                { "id" : "ajson1", "parent" : "#", "text" : "Simple root node" },
                                { "id" : "ajson2", "parent" : "ajson1", "text" : "fuck off node" },
                                { "id" : "ajson3", "parent" : "ajson1", "text" : "whetever node" },
                                { "id" : "ajson4", "parent" : "ajson1", "text" : "fuck this shit node" },                                
                            ]
                }
            });
            var jstree = this.$("#easy-tree").jstree(true);
            var v =this.$("#easy-tree").jstree(true).get_json('#', { 'flat': false });
            console.log('jstree instance  : ',this.$('#easy-tree').jstree(true));
            console.log('tree content json : ',v);

            jstree.settings.contextmenu.items = jstree.settings.contextmenu.items();

            // when needed:
            jstree.settings.contextmenu.items = this.contextmenu.call(this);
            //jstree.settings.contextmenu.items = this.contextmenu.call(this);
            
            
            this.$('#example').DataTable();


            Dropzone.autoDiscover = false;
            //this.$(".dropzone").dropzone({ url: "/home/whatever " });
            Dropzone.options.dropzoneID = {
              paramName: "file", 
              maxFilesize: 25, //MB
              autoProcessQueue: false,
              addRemoveLinks: true,
              maxFiles: 1,
              accept: function(file, done) {
                var reader = new FileReader();
                reader.addEventListener("loadend", function(event) {
                    var widget = new ConfirmWidget(self);
                    widget.on("user_chose", self, self.user_chose);
                    widget.appendTo(self.$el);
                    var data = event.target.result;
                    self.store_dom_value(data);
                    self.$('.dropzone').hide();
                    self.$('.select_file_button').show();
                });
                reader.readAsDataURL(file);
                
              }
            };
        },
        contextmenu: function($node){
            var tree = this.$("#easy-tree").jstree(true);
            var items = {   
                        "Update Alfresco": {
                            "separator_before" : false,
                            "separator_after" : false,
                            "label" : "Create Folder",
                            "action" : function (obj) {
                                alert("OK"); /* this is the tree, obj is the node */ 
                            }
                        },
                    };
            return items;
        },
        on_click: function(){
            var v =this.$("#easy-tree").jstree(true).get_json('#', { 'flat': true });
            console.log('jstree instance  : ',this.$('#easy-tree').jstree(true));
            console.log('tree content json : ',JSON.stringify(v));
        },
        destroy_content: function() {
            console.log('Char destroy_content');
            this.$input = undefined;
            // todo check how to detroy the upload form in order to render it empty for the next redraw
        },
        store_dom_value: function (data) {
            this.internal_set_value(data);
        },
        commit_value: function () {
            console.log('Char commit_value');
            //this.store_dom_value();
            return this._super();
        },
        render_value: function() {
            console.log('Char render_value');
            var show_value = this.format_value(this.get('value'), '');
            console.log('Char render_value show_value = '+show_value);
            if(this.get('value')){
                this.$input.val(this.get('value'));
            }else{
                this.$input.val('empty');
            }

            
            /*if (this.$input) {
                this.$input.val(show_value);
            } else {
                this.$el.text(show_value);
            }*/
        },
        is_syntax_valid: function() {
            if (this.$input) {
                try {
                    this.parse_value(this.$input.val(), '');
                } catch(e) {
                    return false;
                }
            }
            return true;
        },
        parse_value: function(val, def) {
            return formats.parse_value(val, this, def);
        },
        format_value: function(val, def) {
            return formats.format_value(val, this, def);
        },
        is_false: function() {
            return this.get('value') === '' || this._super();
        },
        focus: function() {
            if (this.$input) {
                return this.$input.focus();
            }
            return false;
        },
    });

    core.form_widget_registry.add('upload', UploadField);
    core.form_widget_registry.add('upload_file', SchoolFieldBinaryFile);
});
