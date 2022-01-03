odoo.define('bv_crm_dashboard.crm_dashboard', function (require) {
	"use strict";
	var AbstractAction = require('web.AbstractAction');
	var core = require('web.core');
	var session = require('web.session');
	var QWeb = core.qweb;
	var _t = core._t;

	var BVCRMDashboard = AbstractAction.extend({
		template:'CRMDashboard',
		events: {
			'click .my-pipeline-info':'my_pipeline_info',
			'click .open-opportunities-info':'open_opportunity_info',
			'click .overdue-opportunities-info':'overdue_opportunity_info',
			'click .total-won-info':'total_won_info',
			'click .to-invoice-info':'to_invoice_info',
			'click .lead_details':'lead_details',
			'click .customer_details':'customer_details',
			'click .activity_details':'activity_details',
		},

		start: function() {
			var self = this; 
			self.get_total_lead_opportunity();
			self.get_my_pipeline();
			self.get_open_opportunity();
			self.get_overdue_opportunity();
			self.get_total_won();
			self.get_to_be_invoiced();
			self.get_expected_revenue();
			self.get_lead_opportunity();
			self.get_won_list();
			self.get_activity_type();
			self.get_lost_list();
			self.get_partner_list();
			self.get_top_salesteam_graph();
			self.loss_list_customer_graph();
			self.total_expected_revenue_graph();
			self.count_wise_lead();
			self.top_recent_customer();
			self.won_list_customer();
		},

		won_list_customer: function(){
			var self = this
			self._rpc({
				model: "crm.lead",
				method: "won_list_customer",
				args: [],
				kwargs: {context: session.user_context},
			}).then(function (result) {
				var array_lst = []
				var options = {
					responsive: true
				};
				window.myCharts = new Chart($("#won_list_customer"), {
					type: 'doughnut',
					tooltipFillColor: "rgba(51, 51, 51, 0.55)",
					data: {
						labels: result[1],
						datasets: [{
							data: result[0],
							backgroundColor: [
								'#66ff33 ', '#cc9900 ', '#669900', '#00e600', '#339933'
							],
							hoverBackgroundColor: [
								'#66ff33 ', '#cc9900 ', '#669900', '#00e600', '#339933'
							]
						}]
					},
					options: {
						responsive: true
					}
				});
			});
		},

		top_recent_customer: function(){
			var self = this
			self._rpc({
				model: "crm.lead",
				method: "top_recent_customer",
				args: [],
				kwargs: {context: session.user_context},
			}).then(function (result) {
				var array_lst = []
				var options = {
					responsive: true
				};
				window.myCharts = new Chart($("#top_recent_customer"), {
					type: 'doughnut',
					tooltipFillColor: "rgba(51, 51, 51, 0.55)",
					data: {
						labels: result[1],
						datasets: [{
							data: result[0],
							backgroundColor: [
								'#66aecf ', '#6993d6 ', '#666fcf', '#7c66cf', '#9c66cf'
							],
							hoverBackgroundColor: [
								'#66aecf ', '#6993d6 ', '#666fcf', '#7c66cf', '#9c66cf'
							]
						}]
					},
					options: {
						responsive: true
					}
				});
			});
		},

		count_wise_lead: function(){
			var self = this
			/*var ctx = self.$("#count_wise_lead");*/
			self._rpc({
				model: "crm.lead",
				method: "count_wise_lead",
				args: [],
				kwargs: {context: session.user_context},
			}).then(function (result) {
				var data = {
					labels: result[1],
					datasets: [
					{
						label: '',
						data: result[0],
						backgroundColor: [
							"rgba(0, 204, 204,1)",
							"rgba(51, 153, 255, 1)",
							"rgba(102, 204, 255,1)",
							"rgba(204, 204, 255,1)",
							"rgba(204,204,255,1)"
						],
						borderColor: [
							"rgba(255, 99, 132, 0.2)",
							"rgba(54, 162, 235, 0.2)",
							"rgba(75, 192, 192, 0.2)",
							"rgba(153, 102, 255, 0.2)",
							"rgba(10,20,30,0.3)"
						],
					borderWidth: 1
					},
					]
				};
				//options
				var options = {
					responsive: true,
					itle: {
					display: false,
					position: "top",
					text: "",
					fontSize: 18,
					fontColor: "#111"
					},
					legend: {
						display: false,
						position: "bottom",
						labels: {
							fontColor: "#333",
							fontSize: 16
						}
					},
					scales: {
						yAxes: [{
						ticks: {
							min: 0
						}
					}]
					},
					onClick:function(e){
                            var activePoints = myCharts.getElementsAtEvent(e);
                            if (activePoints.length>0){
                                var selectedIndex = activePoints[0]._index;
                                var target_id = result[2][selectedIndex]
                                self.do_action({
                                    name: _t("CRM Lead"),
                                    type: 'ir.actions.act_window',
                                    res_model: 'crm.lead',
                                    view_mode: 'form',
                                    views: [[false,'list'],[false, 'form']],
                                    domain: [['stage_id', '=', target_id]],
                                    target: 'current',
                                });
                            }
					    },
					onHover: function(event, chartElement){
					     event.target.style.cursor = chartElement[0] ? 'pointer' : 'default';
					},
				};
				var ctx = document.getElementById("count_wise_lead");
				myCharts = new Chart(ctx, {
					type: "bar",
					data: data,
					options: options
					});

			});
		},

		total_expected_revenue_graph: function(){
			var self = this
			/*var ctx = self.$("#total_expected_revenue_graph");*/
			self._rpc({
				model: "crm.lead",
				method: "total_expected_revenue_graph",
				args: [],
				kwargs: {context: session.user_context},
			}).then(function (result) {
				var data = {
					labels: result[1],
					datasets: [
					{
						label: '',
						data: result[0],
						backgroundColor: [
							"rgba(145, 184, 122,1)",
							"rgba(255, 209, 222, 1)",
							"rgba(75, 192, 192,1)",
							"rgba(153, 102, 255,1)",
							"rgba(10,20,30,1)"
						],
						borderColor: [
							"rgba(255, 99, 132, 0.2)",
							"rgba(54, 162, 235, 0.2)",
							"rgba(75, 192, 192, 0.2)",
							"rgba(153, 102, 255, 0.2)",
							"rgba(10,20,30,0.3)"
						],
					borderWidth: 1
					},
					]
				};
				//options
				var options = {
					responsive: true,
					itle: {
					display: false,
					position: "top",
					text: "",
					fontSize: 18,
					fontColor: "#111"
					},
					legend: {
						display: false,
						position: "bottom",
						labels: {
							fontColor: "#333",
							fontSize: 16
						}
					},
					scales: {
						yAxes: [{
						ticks: {
							min: 0
						}
					}]
					}
				};
				window.myCharts = new Chart(self.$("#total_expected_revenue_graph"), {
					type: "bar",
					data: data,
					options: options
					});

			});
		},

		loss_list_customer_graph: function(){
			var self = this
			self._rpc({
				model: "crm.lead",
				method: "loss_list_customer_graph",
				args: [],
				kwargs: {context: session.user_context},
			}).then(function (result) {
				var array_lst = []
				var options = {
					responsive: true
				};
				window.myCharts = new Chart($("#loss_list_customer_graph"), {
					type: 'doughnut',
					tooltipFillColor: "rgba(51, 51, 51, 0.55)",
					data: {
						labels: result[1],
						datasets: [{
							data: result[0],
							backgroundColor: [
								'#cc9900', '#cc3300 ', '#666fcf', '#7c66cf', '#9c66cf'
							],
							hoverBackgroundColor: [
								'#cc9900', '#cc3300 ', '#666fcf', '#7c66cf', '#9c66cf'
							]
						}]
					},
					options: {
						responsive: true
					}
				});
			});
		},

		get_top_salesteam_graph: function(){
			var self = this
			self._rpc({
				model: "crm.lead",
				method: "get_top_salesteam_graph",
				args: [],
				kwargs: {context: session.user_context},
			}).then(function (result) {
				var array_lst = []
				var options = {
					responsive: true
				};
				window.myCharts = new Chart($("#top_sale_team_graph"), {
					type: 'doughnut',
					tooltipFillColor: "rgba(51, 51, 51, 0.55)",
					data: {
						labels: result[1],
						datasets: [{
							data: result[0],
							backgroundColor: [
								'#66aecf ', '#6993d6 ', '#666fcf', '#7c66cf', '#9c66cf'
							],
							hoverBackgroundColor: [
								'#66aecf ', '#6993d6 ', '#666fcf', '#7c66cf', '#9c66cf'
							]
						}]
					},
					options: {
						responsive: true
					}
				});
			});
		},

		get_total_lead_opportunity: function() {
			var self = this;
			self._rpc({
				model: 'crm.lead',
				method: 'get_total_lead_opportunity',
				args: [],
				kwargs: {context: session.user_context},
			}).then(function(result) {
				self.$el.find('#totalLead').html(result);
			});
		},

		get_my_pipeline: function() {
			var self = this;
			self._rpc({
				model: 'crm.lead',
				method: 'get_my_pipeline',
				args: [],
				kwargs: {context: session.user_context},
			}).then(function(result) {
				self.$el.find('#myPipeline').html(result);
			});
		},

		get_open_opportunity: function() {
			var self = this;
			self._rpc({
				model: 'crm.lead',
				method: 'get_open_opportunity',
				args: [],
				kwargs: {context: session.user_context},
			}).then(function(result) {
				self.$el.find("#openOpportunity").html(result);
			});
		},

		get_overdue_opportunity: function() {
			var self = this;
			self._rpc({
				model: 'crm.lead',
				method: 'get_overdue_opportunity',
				args: [],
				kwargs: {context: session.user_context},
			}).then(function(result) {
				self.$el.find("#overdueOpportunity").html(result);
			});
		},

		get_total_won: function() {
			var self = this;
			self._rpc({
				model: 'crm.lead',
				method: 'get_total_won',
				args: [],
				kwargs: {context: session.user_context},
			}).then(function(result) {
				self.$el.find("#totalWon").html(result);
			});
		},

		get_to_be_invoiced: function() {
			var self = this;
			self._rpc({
				model: 'crm.lead',
				method: 'get_to_be_invoiced',
				args: [],
				kwargs: {context: session.user_context},
			}).then(function(result) {
				self.$el.find("#totalInvoice").html(result);
			});
		},

		get_expected_revenue: function() {
			var self = this;
			self._rpc({
				model: 'crm.lead',
				method: 'get_expected_revenue',
				args: [],
				kwargs: {context: session.user_context},
			}).then(function(result) {
				self.$el.find("#expectedRevenue").html(result);
			});
		},

		my_pipeline_info: function(e){
		var self = this;
		this.do_action({
			name: _t("CRM Lead"),
			type: 'ir.actions.act_window',
			res_model: 'crm.lead',
			view_mode: 'tree,kanban,form',
			views: [[false, 'list'],[false, 'kanban'],[false, 'form']],
			context: {'search_default_assigned_to_me':true},
			target: 'current',
			})
		},

		open_opportunity_info: function(e){
		var self = this;
		this.do_action({
			name: _t("CRM Lead"),
			type: 'ir.actions.act_window',
			res_model: 'crm.lead',
			view_mode: 'tree,kanban,form',
			views: [[false, 'list'],[false, 'kanban'],[false, 'form']],
			domain: [['type', '=', 'opportunity'],['probability', '<',100]],
			target: 'current',
			})
		},

		overdue_opportunity_info: function(e){
		var self = this;
		var today_date = new Date();
		this.do_action({
			name: _t("CRM Lead"),
			type: 'ir.actions.act_window',
			res_model: 'crm.lead',
			view_mode: 'tree,kanban,form',
			views: [[false, 'list'],[false, 'kanban'],[false, 'form']],
			domain: [['type', '=', 'opportunity'],['date_deadline', '<', today_date], ['date_closed', '=', false]],
			target: 'current',
			})
		},

		total_won_info: function(e){
		var self = this;
		this.do_action({
			name: _t("CRM Lead"),
			type: 'ir.actions.act_window',
			res_model: 'crm.lead',
			view_mode: 'treekanban,form',
			views: [[false, 'list'],[false, 'kanban'],[false, 'form']],
			domain: [['active', '=', true],['probability', '=', 100]],
			target: 'current',
			})
		},

		to_invoice_info: function(e){
		var self = this;
		this.do_action({
			name: _t("Sale Order"),
			type: 'ir.actions.act_window',
			res_model: 'sale.order',
			view_mode: 'tree,kanban,form',
			views: [[false, 'list'],[false, 'kanban'],[false, 'form']],
			domain: [['invoice_status','=','to invoice']],
			target: 'current',
			})
		},

		get_lead_opportunity: function() {
			var self = this;
			self._rpc({
				model: 'crm.lead',
				method: 'get_lead_opportunity',
				args: [],
				kwargs: {context: session.user_context},
				}).then(function(result) {
				var i;
				var body_html = "";
				for (i = 0; i < result.length; i++) {
					var data = result[i]
					body_html += "<tr class='lead_details' id='"+data['lead_id']+"'><td>"+data['cl_name']+"</td><td>"+data['cl_revenue']+"</td><td>"+data['cl_probability']+"</td></tr>"
				}
				self.$el.find('tbody#top-lead-list').html(body_html);
			});
		},

		// GET top Lead details record
		lead_details: function(e){
		var self = this;
		var target_id = Number(e.currentTarget.id);
		console.log(target_id);
		this.do_action({
			name: _t("Lead details"),
			type: 'ir.actions.act_window',
			res_model: 'crm.lead',
			view_mode: 'form',
			views: [[false,'list'],[false, 'form']],
			domain: [['id', '=', target_id]],
			target: 'current',
			});
		},

		// GET top customer details record
		customer_details: function(e){
		var self = this;
		var target_id = Number(e.currentTarget.id);
		this.do_action({
			name: _t("Customer details"),
			type: 'ir.actions.act_window',
			res_model: 'res.partner',
			view_mode: 'form',
			views: [[false,'list'],[false, 'form']],
			domain: [['id', '=', target_id]],
			target: 'current',
			});
		},

		// GET Activity details record
		activity_details: function(e){
		var self = this;
		var target_id = Number(e.currentTarget.id);
		this.do_action({
			name: _t("Activity details"),
			type: 'ir.actions.act_window',
			res_model: 'mail.activity.type',
			view_mode: 'form',
			views: [[false,'list'],[false, 'form']],
			domain: [['id', '=', target_id]],
			target: 'current',
			});
		},

		get_won_list: function() {
			var self = this;
			self._rpc({
				model: 'crm.lead',
				method: 'get_won_list',
				args: [],
				kwargs: {context: session.user_context},
				}).then(function(result) {
				var i;
				var body_html = "";
				if(result!=null){
                    for (i = 0; i < result.length; i++) {
                        var data = result[i]
                        body_html += "<tr class='lead_details' id='"+data['cl_id']+"'><td>"+data['cl_name']+"</td><td>"+data['cl_probability']+"</td></tr>"
                    }
				}
				self.$el.find('tbody#won-list').html(body_html);
			});
		},

		get_activity_type: function(){
			var self = this;
			self._rpc({
				model: 'crm.lead',
				method: 'get_activity_type',
				args: [],
				kwargs: {context: session.user_context},
				}).then(function(result) {
				var i;
				var body_html = "";
				for (i = 0; i < result.length; i++) {
					var data = result[i]
					body_html += "<tr class='activity_details' id='"+data['mat_id']+"'><td>"+data['activity_name']+"</td></tr>"
				}
				self.$el.find('tbody#activity_type').html(body_html);
			});
		},

		get_lost_list: function() {
			var self = this;
			self._rpc({
				model: 'crm.lead',
				method: 'get_lost_list',
				args: [],
				kwargs: {context: session.user_context},
				}).then(function(result) {
				var i;
				var body_html = "";
				for (i = 0; i < result.length; i++) {
					var data = result[i]
					body_html += "<tr class='lead_details' id='"+data['cl_id']+"'><td>"+data['cl_name']+"</td><td>"+data['cl_probability']+"</td></tr>"
				}
				self.$el.find('tbody#loss-list').html(body_html);
			});
		},

		get_partner_list: function() {
			var self = this;
			self._rpc({
				model: 'crm.lead',
				method: 'get_partner_list',
				args: [],
				kwargs: {context: session.user_context},
				}).then(function(result) {
				var i;
				var body_html = "";
				if(result!=null){
                    for (i = 0; i < result.length; i++) {
                        var data = result[i]
                        body_html += "<tr class='customer_details' id='"+data['customer_id']+"'><td>"+data['partner_name']+"</td><td>"+data['cl_plan_revenue']+"</td></tr>"
                    }
				}
				self.$el.find('tbody#partner-list').html(body_html);
			});
		},

	});

	core.action_registry.add('bv_crm_dashboard', BVCRMDashboard);
	return BVCRMDashboard
});