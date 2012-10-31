$(function(){

	window.Chat = Backbone.Model.extend({
		defaults: function() {
			return {
				messages:  [],
				author: 'unknown',
				datetime: ''
			};
		}
	});

	window.ChatList = Backbone.Collection.extend({
		model: Chat,
		url : "/chats/dzis/0"
	});
	window.List = new ChatList();

	window.ChatView = Backbone.View.extend({
		tagName:  "div",
		template: _.template($('#item-template').html()),
		template_messagge: _.template($('#message-template').html()),

		initialize: function(){
			_.bindAll(this, 'render', 'parseAuthor');
		},
		render: function() {
			this.parseAuthor();
			this.parseMessages();


			$(this.el).html(this.template(this.model.toJSON()));
			return this;
		},
		parseAuthor: function() {
			var author = this.model.get('author').replace(/\@[a-z0-9\.]+/,'').split('.').join(' ');
			author = author.toLowerCase().replace(/\b[a-z]/g, function(letter) {
				return letter.toUpperCase();
			});
			this.model.set('author',author);
		},
		parseMessages: function() {
			var message_body = '';
			for(item in this.model.get('messages')) {
				if(this.model.get('messages').hasOwnProperty(item)) {
					message_body+=this.template_messagge(this.model.get('messages')[item]);
				}
			}
			this.model.set('messages',message_body);
		}
	});
	
	window.AppView = Backbone.View.extend({
		el: $("#chatApp"),
		template: _.template($('#menu-template').html()),
		template_more: _.template($('#more-template').html()),
		events: {
			"click #load-more" : "loadMore"
		},
		initialize: function() {
			_.bindAll(this, 'render', 'appendItem');
  			
			this.render();

			List.bind('add', this.appendItem, this);
			List.add(chatsItems);
		//List.fetch({"add":true, data: {"ajax":1}});
		},
		appendItem: function(item) {
			var view = new ChatView({model: item});
			$(this.el).append(view.render().el);
		},
		loadMore: function() {
			console.log(1);
		},
		render: function() {
			$(this.el).append(this.template());
			$("#more").append(this.template_more());
			return this;
		}
	});
	window.App = new AppView;
});