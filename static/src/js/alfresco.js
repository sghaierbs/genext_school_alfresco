odoo.define('genext_school_alfresco.alfresco', function(require){
    "use strict";
    var core = require('web.core');
    var QWeb = core.qweb;
    var common = require('web.form_common');
    var formats = require('web.formats');
    var framework = require('web.framework');
    var FieldChar = core.form_widget_registry.get('char');
    var FieldBinaryFile = core.form_widget_registry.get('binary');
    
    var Widget = require('web.Widget');
    var Model = require('web.Model');
    var Data = require('web.data');
    var Dialog = require('web.Dialog');
    var NotificationManager = require('web.notification').NotificationManager;
    var _t = core._t;



    var UploadNewDocumentDialog = Dialog.extend({
        template: 'UploadNewDocumentDialog',
        events: {
            'change input.new-upload':'load_file',
        },
        init: function(parent, params) {
            this._super(parent);
            self = this;
            this.fileObject = new Array();
            this.fileObject['docLibNodeRef'] = parent.view.datarecord.document_library_node_ref
            var model = new Model('school.student');
            model.call("get_folders").then(function(paths) {
                var dateObj = new Date();
                var month = dateObj.getUTCMonth() + 1; //months from 1-12
                var day = dateObj.getUTCDate();
                var year = dateObj.getUTCFullYear();
                var i;
                for(i=0 ; i < paths.length; i++){
                    if(paths[i].data.is_dynamic){
                        var path = paths[i].data.path;
                        path = path.replace(/documentLibrary\//,'')
                        path = path.replace(/\|year\|/,year)
                        path = path.replace(/\|month\|/,month)
                        path = path.replace(/\|day\|/,day)

                        var folderName = paths[i].text;
                        folderName = folderName.replace(/\|year\|/,year)
                        folderName = folderName.replace(/\|month\|/,month)
                        folderName = folderName.replace(/\|day\|/,day)
                        var itemval= '<option value="'+path+'">'+folderName+'</option>';
                        console.log(itemval);
                        self.$('.paths').append(itemval);
                    }else{
                        var path = paths[i].data.path;
                        path = path.replace(/documentLibrary\//,'')
                        var itemval= '<option value="'+path+'">'+paths[i].text+'</option>';
                        console.log(itemval);
                        self.$('.paths').append(itemval);
                    }
                }
                console.log(paths);
            });
            var options = {
                buttons: [
                        {
                            text: _t("Save"),
                            classes: "btn-primary",
                            click: function () {
                                if(self.$('.base64').val() && self.$('.new-upload').val()){
                                    self.fileObject['path'] = $(".paths option:selected").val();
                                    self.fileObject['description'] = $(".description").val();
                                    if(self.$('.file_name').val())
                                        self.fileObject['filename'] = self.$('.file_name').val()
                                    if(self.$('.file_title').val())
                                        self.fileObject['fileTitle'] = self.$('.file_title').val()
                                    self.upload_file(self.fileObject);
                                    parent.tree.refresh();
                                }else{
                                    self.fileObject['path'] = $(".paths option:selected").val();
                                    console.log('ELSE',self.fileObject);
                                }
                                self.$el.parents('.modal').modal('hide');
                            }
                        },
                        {
                            text: _t("Close"),
                            click: function () { 
                                self.$el.parents('.modal').modal('hide');
                            }
                        },
                 ],
                close: function () { 
                    self.close();
                }
            };

            this._super(parent, options);
            this.set_title(_t("upload document"));
        },
        renderElement: function() {
            this._super();
        },
        upload_file: function(fileObject){
            console.log('fileObject: ',fileObject)
            console.log('self.fileObject: ',self.fileObject)
            var model = new Model('school.student');
            model.call("uploadFile",[fileObject.filename, fileObject.fileTitle, fileObject.base64, fileObject.path,fileObject.description, fileObject.docLibNodeRef]).then(function(response) {
                console.log('server response: ',response);
            });
        },
        load_file: function(event){
            console.log(event)
            var file  = event.target.files[0];
            var reader = new FileReader();
            reader.newFile = file;
            reader.addEventListener("loadstart", function(event) {
                framework.blockUI();
                console.log('loading just started');
            });
            reader.addEventListener("loadend", function(event) {
                console.log(event.target.newFile);
                var data = event.target.result;
                var base64result = data.substr(data.indexOf(',') + 1);
                //var base64result = data;
                console.log(base64result);
                self.fileObject['filename'] = event.target.newFile.name
                self.fileObject['type'] = event.target.newFile.type
                self.fileObject['base64'] = base64result
                self.$('.base64').val(base64result);
                framework.unblockUI();
                console.log('loading just ended');
            });
            reader.readAsDataURL(file);
        },
        close: function() {
            this._super();
        }
     });



    var UploadNewDocumentVersionDialog = Dialog.extend({
        template: 'UploadNewDocumentVersionDialog',
        events: {
            'change input.new-upload':'load_file',
        },
        init: function(parent, params) {
            this._super(parent);
            self = this;
            console.log('new version: params', params);
            this.fileObject = new Array();
            this.fileObject['nodeRef'] = params.id;
            var options = {
                buttons: [
                        {
                            text: _t("Save"),
                            classes: "btn-primary",
                            click: function () {
                                if(self.$('.base64').val() && self.$('.new-upload').val()){
                                    self.fileObject['version'] = $(".version option:selected").val();
                                    if(self.$('.comments').val())
                                        self.fileObject['comments'] = self.$('.comments').val();
                                    self.upload_file(self.fileObject);
                                }else{
                                    console.log('ELSE',self.fileObject);
                                }
                                self.$el.parents('.modal').modal('hide');
                            }
                        },
                        {
                            text: _t("Close"),
                            click: function () { 
                                self.$el.parents('.modal').modal('hide');
                            }
                        },
                 ],
                close: function () { 
                    self.close();
                }
            };

            this._super(parent, options);
            this.set_title(_t("upload new version"));
        },
        renderElement: function() {
            this._super();
        },
        upload_file: function(fileObject){
            console.log('fileObject: ',fileObject)
            console.log('self.fileObject: ',self.fileObject)
            var model = new Model('school.student');
            model.call("uploadNewVersion",[fileObject.filename, fileObject.base64,fileObject.nodeRef, fileObject.comments, fileObject.version]).then(function(response) {
                console.log('server response: ',response);
            });
        },
        load_file: function(event){
            console.log(event)
            var file  = event.target.files[0];
            var reader = new FileReader();
            reader.newFile = file;
            reader.addEventListener("loadstart", function(event) {
                framework.blockUI();
                console.log('loading just started');
            });
            reader.addEventListener("loadend", function(event) {
                console.log(event.target.newFile);
                var data = event.target.result;
                var base64result = data.substr(data.indexOf(',') + 1);
                //var base64result = data;
                console.log(base64result);
                self.fileObject['filename'] = event.target.newFile.name
                self.fileObject['type'] = event.target.newFile.type
                self.fileObject['base64'] = base64result
                self.$('.base64').val(base64result);
                framework.unblockUI();
                console.log('loading just ended');
            });
            reader.readAsDataURL(file);
        },
        close: function() {
            this._super();
        }
     });




    var DirectoryTree = common.AbstractField.extend(common.ReinitializeFieldMixin, {
        template: 'DirectoryTree',
        events: {
            'change': 'store_dom_value',
        },
        init: function (field_manager, node) {
            this._super(field_manager, node);
            this.on('jstree_dialog',this,this.on_jstree_dialog);
        },
        initialize_content: function() {
            self = this;
            var fieldValue = this.get('value');
            if(fieldValue){
                if(this.is_json(fieldValue) && JSON.parse(fieldValue).length > 0)
                    this.treeData = JSON.parse(fieldValue);
                else
                    this.treeData = [{ "id" : "doclib", "parent" : "#", "text" : "documentLibrary", 
                                        'data':{
                                            "name" : "documentLibrary",
                                            'path':'/',
                                            'is_container':false ,
                                            'is_dynamic':false,
                                            'naming_pattern':'',
                                        } 
                                    }];
            }else
                this.treeData = [{ "id" : "doclib", "parent" : "#", "text" : "documentLibrary", 
                                        'data':{
                                            "name" : "documentLibrary",
                                            'path':'/',
                                        'is_container':false ,
                                        'is_dynamic':false,
                                        'naming_pattern':'',
                                    } 
                                }];
            this.$('#tree').jstree({
                'core' : {
                    "check_callback" : true,
                    'data' : self.treeData,
                },
                "plugins" : ["contextmenu","dnd","unique","types"],
                "contextmenu": {"items": this.contextmenu},
                "dnd": { "is_draggable": this.is_draggable.call(self) },
                "types" : {
                    "#" : {"max_children" : 1},
                },
            });
            this.tree = this.$('#tree').jstree(true);
        },
        load_data: function(node,callback){
            if (node.id == "#"){
                console.log("if");
                callback.call(this,[{ "id" : "doclib", "parent" : node.id, "text" : "root","state": {"loaded": false}, "children" : true }]);
            }else{
                console.log("else");
                callback.call(this,[{ "id" : node.id+node.id, "parent" : node.id, "text" : "root","state": {"loaded": false}, "children" : true }]);
            }
        },
        load_children: function(){

        },
        contextmenu: function(node){
            var tree = $('#tree').jstree(true);
            // The default set of all items
            var items = {
                "Create": {
                    "separator_before": false,
                    "separator_after": false,
                    "label": "Create",
                    "action": function (obj) { 
                        self.trigger('jstree_dialog',{"obj":obj,"tree":tree,"node":node});
                    }
                },
                "Edit": {
                    "separator_before": false,
                    "separator_after": false,
                    "label": "Edit",
                    "action": function (obj) { 
                        self.trigger('jstree_dialog',{"obj":obj,"tree":tree,"node":node});
                    }
                },
                "Remove": {
                    "separator_before": true,
                    "separator_after": false,
                    "label": "Remove",
                    "action": function (obj) { 
                        if(confirm('Are you sure to remove this category?')){
                            tree.delete_node(node);
                        }
                    }
                }
            };
            if(self.get('effective_readonly'))
                return {};
            else
                return items;
        },
        on_jstree_dialog: function(params){
            var dialog = new CreateFolderDialog(self,params);
            dialog.open();
        },
        destroy_content: function() {
            console.log('Char destroy_content');
            this.$input = undefined;
            this.tree = undefined;
        },
        store_dom_value: function () {
            var v =self.$("#tree").jstree(true).get_json('#', { 'flat': true });
            console.log('Char store_dom_value');
            this.internal_set_value(JSON.stringify(v));
            console.log('tree content json : ',JSON.stringify(v));
        },
        commit_value: function () {
            console.log('Char commit_value');
            this.store_dom_value();
            return this._super();
        },
        render_value: function() {
            self = this;
            if(this.get('effective_readonly')){
                this.$('#tree').bind('ready.jstree', function(e, data) {
                    $('#tree >ul > li').each( function() {
                       self.disable.call(self,this.id );        
                    });
                 });
            }
        },
        disable: function(node_id) {
            self = this;
            var node = this.tree.get_node(node_id);
            this.tree.disable_node(node); 
            node.children.forEach( function(child_id) {            
                self.disable(child_id);
            });
        },
        is_draggable: function(){
            if(this.get('effective_readonly'))
                return false;
            else
                return true;
        },
        is_json: function(str) {
            try {
                JSON.parse(str);
            } catch (e) {
                return false;
            }
            return true;
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

    core.form_widget_registry.add('DirectoryTree', DirectoryTree);


    var Alfresco = common.AbstractField.extend(common.ReinitializeFieldMixin, {
        template: 'Alfresco',
        datatable: null,
        events: {
            'change': 'store_dom_value',
            'click td.details-control': 'render_row_details',
            'click a.content-action-open-alfresco': 'on_open_in_alfresco',
            'click a.content-action-download': 'on_content_download',
            'click button.content-action-preview': 'display_document_preview',
            'click button.action-upload-new-version': 'on_upload_new_version',
           // 'click button.action-version': 'on_version_history',
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
            /*this.notification_manager = new NotificationManager(this);
            this.notification_manager.appendTo(this.$el);
            this.notification_manager.notify('SBS', 'whatever', true);
            this.folders = false;
            console.log('this ',this);
            console.log('view ',this.view);
            console.log('dataset ',this.view.dataset);
            console.log('datarecord ',this.view.datarecord);
            console.log('dataset.model ',this.view.dataset.model);
            console.log('datarecord.id ',this.view.datarecord.id);*/
            //this.view.dataset.write(this.view.datarecord.id, {name:'new Value',test_field:'hahaha'});
            var self = this;
            this.$('.select_file_button').hide();
            this.$('.select_file_button').click(this.on_click);

            // check if this field contains the documentLibrary nodeRef 
            if(this.get('value')){
                this.$('#tree').jstree({
                    'core' : {
                        "check_callback" : true,
                        'data' : function(node,callback){
                            if (node.id == "#"){
                                var model = new Model('school.student');
                                model.call("getNode",[self.view.datarecord.document_library_node_ref]).then(function(node) {
                                    var doclib = { "id" : node.id, "parent" : "#", "text" : node.name,"state": {"loaded": false}, "children" : true }
                                    callback.call(this,[doclib]);
                                });
                            }else{
                                //self.$('#tree').jstree(true).set_icon(node, "/genext_school_alfresco/static/src/css/images/folder-64.png");;
                                var model = new Model('school.student');
                                console.log('content of node: ', node);
                                model.call("getNodeChildren",[node.id]).then(function(nodes) {
                                    var childNodes = [];
                                    for(var i = 0; i < nodes.length; i++) {
                                        var alfrNode = nodes[i].entry;
                                        childNodes.push({"id" :alfrNode.id, "parent" :node.id, "text" :alfrNode.name, "state":{"loaded": false}, "children" : true, 'type':'newType' });
                                    }
                                    callback.call(this,childNodes);
                                });
                            }
                        },
                    },
                });
                this.tree = this.$('#tree').jstree(true);
                $("#tree").bind("select_node.jstree", this.on_node_select);
            
                var dataSet = [
                   /* [ "Tiger Nixon", "System Architect", "Edinburgh", "5421", "2011/04/25", "$320,800" ,'<button type="button" class="btn btn-default btn-xs content-action-preview alfresco-btn" data-toggle="tooltip" title="Preview" aria-label="Preview"> <span class="glyphicon glyphicon-refresh"  aria-hidden="true"></span> </button>'],
                    [ "Garrett Winters", "Accountant", "Tokyo", "8422", "2011/07/25", "$170,750","" ],
                    [ "Ashton Cox", "Junior Technical Author", "San Francisco", "1562", "2009/01/12", "$86,000" ,""],
                    [ "Cedric Kelly", "Senior Javascript Developer", "Edinburgh", "6224", "2012/03/29", "$433,060","" ],
                    [ "Airi Satou", "Accountant", "Tokyo", "5407", "2008/11/28", "$162,700" ,""]*/
                ];
                /*
                If you are upgrading from DataTables 1.9 or earlier, you might notice that a capital D is used to initialise the DataTable here. 
                $().DataTable() returns a DataTables API instance, while $().dataTable() will also initialise a DataTable, but returns a jQuery object.
                */
                this.datatable = this.$('#example').DataTable({
                    "dom": '<"toolbar">frtip',
                    'data': dataSet,
                    'columnDefs': [{ 'targets':[6], 'visible': false}],
                    'columns': [
                        {
                            "className":      'details-control',
                            "orderable":      false,
                            "data":           null,
                            "defaultContent": '<div class="fa fa-plus-circle"/>'
                        },
                        {'title':'Name'},
                        {'title':'Created by'},
                        {'title':'Created at'},
                        {'title':'Modified at'},
                        {'title':'Action'},
                        {'title':'FileObject'},
                    ],
                    "language": {
                      "emptyTable": "No document available"
                    }
                });
                //this.$("div.toolbar").append('<button type="button" class="btn btn-default btn-xs content-action-preview alfresco-btn" data-toggle="tooltip"  title="Preview" aria-label="Preview"> <span class="glyphicon glyphicon-refresh"  aria-hidden="true"></span> </button>');
                //this.$("div.toolbar").append('<button type="button" class="btn btn-default btn-xs content-action-upload alfresco-btn" data-toggle="tooltip" data-folder-id="" title="Preview" aria-label="Preview"> <span class="fa fa-plus-square-o"  aria-hidden="true"></span> Upload document</button>');

                this.$("div.toolbar").append('<button type="button" class="btn btn-primary btn-sm new-upload">'+
                    '<span class="fa fa-upload" aria-hidden="true"></span> Upload new document'+
                '</button>');

                // in order to obtain the datatable reference you need to call .dataTable() function not the DataTable() constructor
                this.JQdataTable = this.$('#example').dataTable();
                
               /* console.log('Content of site id ',this.view.datarecord.site_id[0]);

                var siteModel = new Model("school.site");
                siteModel.query().filter([['id', '=', this.view.datarecord.site_id[0]]]).all().then(function (site) {
                    console.log('Content of site : ',site);
                });
                */

            }else{
                this.$el.append('<div>No document related to this student found</div>');
            }
            this.$('.new-upload').click(function(){
                self.upload_new_document.apply(self);
            });

            this.$('div.tab_actions button.action-upload').click(function(){
                
            });

        },
        on_version_history: function(){
            console.log('show version history');
            var dialog = new DocumentVersionsHistoryDialog(this,'string');
            dialog.open();
        },
        on_upload_new_version: function(event){
            console.log('uploading new document version');
            var row = this._get_event_row(event);
            var tr = $(row.node());           
            // id: 6 represent the ObjectFile "jsonstring" from alfresco 
            var file_json_string = this.datatable.cell(row.index(),6).data();
            var fileObject = JSON.parse(file_json_string);
            console.log('###### ',fileObject)
            var dialog = new UploadNewDocumentVersionDialog(this,fileObject);
            dialog.open();
        },
        upload_new_document: function(){
            var dialog = new UploadNewDocumentDialog(this,'string');
            dialog.open();
        },
        register_events: function(){

        },
        /**
         * Return the DataTable row on which the event has occured
         */
        _get_event_row: function(e){
            return this.datatable.row($(e.target).closest('tr'));
        },
        render_row_details: function(event){
            var row = this._get_event_row(event);
            var tr = $(row.node());
            tr.find('td.details-control div').toggleClass('fa-minus fa-plus-circle');
            if ( row.child.isShown() ) {
                // This row is already open - close it
                row.child.hide();
            } else {
                // id: 6 represent the ObjectFile "jsonstring" from alfresco 
                var file_json_string = this.datatable.cell(row.index(),6).data();
                var fileObject = JSON.parse(file_json_string);
                fileObject.content.sizeInBytes = this.formatBytes(fileObject.content.sizeInBytes);
                console.log('###### ',fileObject);
                row.child(QWeb.render("ContentDetails", {object: fileObject})).show();
            }
        },
        display_document_preview: function(event){
            var self = this;
            var row = this._get_event_row(event);
            var file_json_string = this.datatable.cell(row.index(),6).data();
            var fileObject = JSON.parse(file_json_string);

            var width="100%";
            var height =  '' + this.$el.height() - 30 + 'px'; //' ' + (H - r.top) + 'px';
            var $document_preview = this.$el.find(".documentpreview");
            $document_preview.empty();
            var googleDocUrl = 'https://docs.google.com/viewer?embedded=true&url='+fileObject.previewUrl;        
            $document_preview.append(QWeb.render("DocumentViewer", {
                                                                        'url': fileObject.previewUrl,
                                                                        'width': width,
                                                                        'height': height,
                                                                        }));

            // Show the previewer
            var $tables_wrapper = this.$el.find('#example'); 
            $tables_wrapper.fadeOut(400, function() {
                $document_preview.fadeIn(400, function() {
                });
            });

            // Attach an event to the "Back to document" icon
            $document_preview.find(".button-back-browser").on('click', function() {
                $document_preview.fadeOut(400, function() {
                    $tables_wrapper.fadeIn();
                });
            });
        },
        on_content_download: function(event){
            /*var self = this;
            console.log('content of e.target : ',$(event.target));
            var row = this._get_event_row(event);
            var file_json_string = this.datatable.cell(row.index(),6).data();
            var fileObject = JSON.parse(file_json_string);
            var model = new Model('school.student');
            model.call("getNodeContent",[fileObject.id]).then(function(response) {
                console.log('Node content ',response);
                $('a.content-action-download').attr("href",response[1]);
            });*/
        },
        on_open_in_alfresco: function(event){
            var self = this;
            var row = this._get_event_row(event);
            var file_json_string = this.datatable.cell(row.index(),6).data();
            var fileObject = JSON.parse(file_json_string);
            // used to prevent popup blocking. 
            // window.open needs to be handled in the main event !!
            var newTabWindow = window.open('', '_blank');
            var model = new Model('school.student');
            model.call("getNodeShareUrl",[fileObject.id]).then(function(response) {
                if(response.success == true)
                    newTabWindow.location = response.result.url;
                else
                    Dialog.alert(self,"Unable to open this document in alfresco, Alfresco response error ");
            });
        },
        on_node_select: function(evnt, data){
            var self = this;
            console.log('event ',evnt);
            console.log('data ',data);
            console.log('dataTable ',this.datatable);

            var fileList = new Array();
            var model = new Model('school.student');
            self.JQdataTable.fnClearTable();
            model.call("getNodeChildren",[data.node.id,false,['properties','allowableOperations']]).then(function(files) {
                console.log('FILES: ',files);
                for(var i = 0; i < files.length; i++) {
                    var file = files[i].entry;
                    console.log('------------------- filename: ',file.name);
                    fileList.push([
                        'for expand btn',
                        file.name,
                        file.createdByUser.displayName,
                        file.createdAt,
                        file.modifiedAt,
                        QWeb.render("ContentActions", {object: file}),
                        JSON.stringify(file),
                    ]);
                }
                console.log('fileList: ',fileList);
                if(fileList.length)
                    self.JQdataTable.fnAddData(fileList,true);
            });
        },
        init_folder_list: function(folders){
            this.folders = folders;
            console.log('thissss : ',this.folders);
            console.log('foledrsss : ',folders);
            var folderOptionList = "";
            for(var i = 0; i < this.folders.length; i++) {
                folderOptionList += "<option value='" + this.folders[i].id + "'>" + this.folders[i].text + "</option>";
            }
            //this.$('select[name="folder"]').append(folderOptionList);
        },
        on_click: function(){
            var self = this;
            var siteModel = new Model("school.site");
            siteModel.query().filter(['id', '=', this.view.datarecord.site_id]).all().then(function (site) {
                console.log('Content of site : ',site);
            });
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
            /*if (this.$input) {
                this.$input.val(show_value);
            } else {
                this.$el.text(show_value);
            }*/
        },
        formatBytes: function(fileSizeInBytes) {
            var i = -1;
            var byteUnits = [' kB', ' MB', ' GB', ' TB', 'PB', 'EB', 'ZB', 'YB'];
            do {
                fileSizeInBytes = fileSizeInBytes / 1024;
                i++;
            } while (fileSizeInBytes > 1024);

            return Math.max(fileSizeInBytes, 0.1).toFixed(1) + byteUnits[i];
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

    core.form_widget_registry.add('Alfresco', Alfresco);



    var CreateFolderDialog = Dialog.extend({
         template: 'CreateFolderDialog',
         init: function(parent, params) {
            this._super(parent);
            this.tree = params.tree;
            this.node = params.node;
            this.obj = params.obj;
            var self = this;
            var options = {
                buttons: [
                        {
                            text: _t("Save"),
                            classes: "btn-primary",
                            click: function () {
                                var result = false;
                                if(this.obj.item.label == "Create"){
                                    result = self.on_click_create();    
                                }else if(this.obj.item.label == "Edit"){
                                    result = self.on_click_update();    
                                }
                                if(result)
                                    self.$el.parents('.modal').modal('hide');
                            }
                        },
                        {
                            text: _t("Close"),
                            click: function () { 
                                self.$el.parents('.modal').modal('hide');
                            }
                        },
                 ],
                close: function () { 
                    self.close();
                }
             };
             this._super(parent, options);
             this.set_title(_t(this.obj.item.label+" Folder"));
        },
        renderElement: function() {
            this._super();
            if(this.obj.item.label == "Edit"){
                this.init_forme(this.node);
            }
            this.$("#is_dynamic").click(function(){
                if($(this).is(':checked')){
                    $("#naming_pattern_div").removeClass('hidden');
                } else {
                    $("#naming_pattern_div").addClass('hidden');
                }
            });
            this.$('#folder_name').on("change paste keyup", function() {
                if($(this).val().match(  /(^[ \"\*\\\>\<\?\/\:\|])|(.[\"\*\\\>\<\?\/\:\|].)|(.[\.]?.[\.]$)|(.*[ \"\*\\\>\<\?\/\:\|]+$)/   )){
                    $(this).addClass("invalid-input");
                    //Dialog.alert(self,"Not allowed names: begins or ends whith white spaces and contains | /  \\  :  >  <  * ");                    
                }else{
                    $(this).removeClass("invalid-input");
                }
            });
        },
        init_forme: function(node){
            this.$("#content_description").val(node.text);
            if(node.data){
                this.$("#folder_name").val(node.data.name);
                this.$("#is_container").prop('checked', node.data.is_container);
                this.$("#is_dynamic").prop('checked', node.data.is_dynamic);
                if(node.data.is_dynamic){
                    this.$("#naming_pattern_div").removeClass('hidden');
                    this.$('#naming_pattern option[value='+node.data.naming_pattern.toLowerCase()+']').attr('selected','selected');
                    node.data.name = node.data.name.replace(/([\-\|].*)|([\|].*)/, "");
                    this.$("#folder_name").val(node.data.name);
                }
            }
        },
        on_click_create: function() {
            var self = this;
            var content_description = this.$("#content_description").val();
            var folder_name = this.$("#folder_name").val();
            var is_container = this.$("#is_container").is(':checked');
            var is_dynamic = this.$("#is_dynamic").is(':checked');
            var naming_pattern = this.$("#naming_pattern").val();
            // Not allowed characters /, \, :, >, <, *, and starts or ends with white space
            if(folder_name.match(  /(^[ \"\*\\\>\<\?\/\:\|])|(.[\"\*\\\>\<\?\/\:\|].)|(.[\.]?.[\.]$)|(.*[ \"\*\\\>\<\?\/\:\|]+$)/  )){
                Dialog.alert(self,"Not allowed names: begins or ends whith white spaces and contains | /  \\  :  >  <  * ");
                return false;
            }else{
                if(is_dynamic){
                    if(folder_name.length)
                        folder_name = folder_name+"-|"+naming_pattern+"|";
                    else
                        folder_name = "|"+naming_pattern+"|";
                }else if(folder_name.length == 0){
                    Dialog.alert(self,"Folder name can be empty only if it's set to dynamic");
                    return false;
                }
                if(content_description.length == 0){
                    Dialog.alert(self,"Content description connot be empty");
                    return false;   
                }
                var folder = {'text' : content_description, 
                                'data': {
                                    'name':folder_name,
                                    'is_container':is_container ,
                                    'is_dynamic':is_dynamic ,
                                    'naming_pattern':naming_pattern,
                                    'path': '' 
                                }
                            };
                var node_id = this.tree.create_node(this.node,folder);
                var new_node = this.tree.get_node(node_id);
                new_node.data.path = this.get_node_full_path(this.tree, new_node);
                console.log('create node after path : ',new_node);
                this.tree.redraw(true);
                return true;
            }
        },
        on_click_update: function() {
            var self = this;
            var content_description = this.$("#content_description").val();
            var folder_name = this.$("#folder_name").val();
            var is_container = this.$("#is_container").is(':checked');
            var is_dynamic = this.$("#is_dynamic").is(':checked');
            var naming_pattern = this.$("#naming_pattern").val();
            // Not allowed characters /, \, :, >, <, *, and starts or ends with white space
            if(content_description.length == 0){
                Dialog.alert(self,"Content description connot be empty");
                return false;   
            }
            if(folder_name.match(  /(^[ \"\*\\\>\<\?\/\:\|])|(.[\"\*\\\>\<\?\/\:\|].)|(.[\.]?.[\.]$)|(.*[ \"\*\\\>\<\?\/\:\|]+$)/  )){
                Dialog.alert(self,"Not allowed names: begins or ends whith white spaces and contains | /  \\  :  >  <  * ");
                return false;
            }else{
                if(is_dynamic){
                    if(folder_name.length)
                        folder_name = folder_name+"-|"+naming_pattern+"|";
                    else
                        folder_name = "|"+naming_pattern+"|";
                }
                this.node.text = content_description;
                this.node.data.name = folder_name
                this.node.data.is_container = is_container;
                this.node.data.is_dynamic = is_dynamic;
                this.node.data.naming_pattern = naming_pattern;
                this.node.data.path = this.get_node_full_path(this.tree,this.node);
                this.tree.redraw(true);
                return true;
            }
        },
        get_node_full_path: function(tree, node){
            var tmp_node = node;
            var path = "";
            var first = true;
            while(tmp_node.id != "#"){
                if(first){
                    path = tmp_node.data.name;
                    first = false;
                }else
                    path = tmp_node.data.name+"/"+path

                tmp_node = tree.get_node(tmp_node.parent);
            }
            console.log('path: ',path)
            return path;
        },
        close: function() {
            this._super();
        }
     });
});

