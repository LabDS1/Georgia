odoo.define('bv_modern_dashboard.purchase_dashboard', function (require) {
	"use strict";
	 
	var AbstractAction = require('web.AbstractAction');
	var core = require('web.core');
	var QWeb = core.qweb;
	var session = require('web.session');
	var _t = core._t;
	 
	var BVPurchaseDashboard = AbstractAction.extend({
		template: 'PurchaseDashboard',
		events: {
			'click .rfqs-info':'rfqs_info',
			'click .purchase-order-info':'purchase_orders_info',
			'click .rfq-sent-info':'rfq_sent_info',
			'click .purchase-cancel-info':'purchase_cancel_info',
			'click .venodrs-info': 'vendors_info',
			'click .to-be-shipped-info': 'to_be_shipped',
			'click .fully-shipped-info': 'fully_shipped',
			'click .fully-billed-info': 'fully_billed',
			'click .purchase_order_details': 'purchase_order_details',
		},  

		start: function() {
			var self = this; 
			self.get_rfqs_count();
			self.get_total_purchase_order_count();
			self.get_rfq_sent_count();
			self.get_purchase_cancel_count();
			self.get_vendors_lst();
			self.get_to_be_shipped_count();
			self.get_fully_shipped_count();
			self.get_fully_billed_count();
			self.get_top_purchase_orders();
			self.get_cancel_purchase_orders();
			self.get_purchase_orders_fully_billed();
			self.get_recent_vendores_graph();
			self.get_top_10_purchase_order_graph();
			self.get_supplier_info_graph();
			self.amount_wise_purchase_order_ac_to_vendor();
			// self.get_supplier_price_graph();
		},

		get_supplier_info_graph:function(){
			var self = this
			/*var ctx = self.$("#vendor_pricelists");*/
			self._rpc({
				model: "product.supplierinfo",
				method: "get_supplier_graph",
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
							"rgba(153, 255, 102,1)",
							"rgba(255, 255, 0, 1)",
							"rgba(255, 204, 102,1)",
							"rgba(204, 102, 0,1)",
							"rgba(255,153,153,1)"
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

				//create Chart class object
				// if (window.myCharts != undefined)
				//     window.myCharts.destroy();
				window.myCharts = new Chart(self.$("#vendor_pricelists"), {
					type: "bar",
					data: data,
					options: options
					});

			});
		},

		amount_wise_purchase_order_ac_to_vendor:function(){
			var self = this
			/*var ctx = self.$("#amount_wise_purchase_order_ac_to_vendor");*/
			self._rpc({
				model: "purchase.order",
				method: "amount_wise_purchase_order_ac_to_vendor",
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

				//create Chart class object
				// if (window.myCharts != undefined)
				//     window.myCharts.destroy();
				window.myCharts = new Chart(self.$("#amount_wise_purchase_order_ac_to_vendor"), {
					type: "bar",
					data: data,
					options: options
					});

			});
		},

		get_top_10_purchase_order_graph: function(){
			var self = this
			self._rpc({
				model: "purchase.order",
				method: "get_top_10_purchase_order",
				args: [],
				kwargs: {context: session.user_context},
			}).then(function (result) {
				var options = {
					responsive: true
				};
				// if (window.donut != undefined)
				//     window.donut.destroy();
				var ctx = document.getElementById("top_10_purchase_order_graph");
				var myCharts = new Chart(ctx, {
					type: 'doughnut',
					tooltipFillColor: "rgba(51, 51, 51, 0.55)",
					data: {
						labels: result[1],
						datasets: [{
							data: result[0],
							backgroundColor: [
								'#1f1f7a', '#ff0066 ', '#ff8000', '#86b300', '#00e600'
							],
							hoverBackgroundColor: [
								'#1f1f7a ', '#ff0066 ', '#ff8000', '#86b300', '#00e600'
							]
						}]
					},
					options: {
						responsive: true,
						onClick:function(e){
                            var activePoints = myCharts.getElementsAtEvent(e);
                            if (result!=null && activePoints.length>0){
                                var selectedIndex = activePoints[0]._index;
                                var target_id = result[2][selectedIndex]
                                self.do_action({
                                    name: _t("Purchase Order"),
                                    type: 'ir.actions.act_window',
                                    res_model: 'purchase.order',
                                    view_mode: 'form',
                                    views: [[false,'list'],[false, 'form']],
                                    domain: [['id', '=', target_id]],
                                    target: 'current',
                                });
                            }
					    },
					    onHover: function(event, chartElement){
					        event.target.style.cursor = chartElement[0] ? 'pointer' : 'default';
					    },
					}
				});
			});
		},

		get_recent_vendores_graph: function(){
			var self = this
			self._rpc({
				model: "purchase.order",
				method: "recent_vendores_graph",
				args: [],
				kwargs: {context: session.user_context},
			}).then(function (result) {
				var options = {
					responsive: true
				};
				// if (window.donut != undefined)
				//     window.donut.destroy();
				var ctx = document.getElementById("recent_vendors_graph");
				var myCharts = new Chart(ctx, {
					type: 'doughnut',
					tooltipFillColor: "rgba(51, 51, 51, 0.55)",
					data: {
						labels: result[1],
						datasets: [{
							data: result[0],
							backgroundColor: [
								'#4ce600', '#ff6666 ', '#ffbb33', '#cc3300', '#993333'
							],
							hoverBackgroundColor: [
								'#4ce600 ', '#ff6666 ', '#ffbb33', '#cc3300', '#993333'
							]
						}]
					},
					options: {
						responsive: true,
						onClick:function(e){
                            var activePoints = myCharts.getElementsAtEvent(e);
                            if (result!=null && activePoints.length>0){
                                var selectedIndex = activePoints[0]._index;
                                var target_id = result[2][selectedIndex]
                                self.do_action({
                                    name: _t("Purchase Order"),
                                    type: 'ir.actions.act_window',
                                    res_model: 'purchase.order',
                                    view_mode: 'form',
                                    views: [[false,'list'],[false, 'form']],
                                    domain: [['partner_id', '=', target_id], ['state', '=', 'purchase']],
                                    target: 'current',
                                });
                            }
					    },
					    onHover: function(event, chartElement){
					        event.target.style.cursor = chartElement[0] ? 'pointer' : 'default';
					    },
					}
				});
			});
		},

		get_rfqs_count: function() {
			var self = this;
			self._rpc({
				model: 'purchase.order',
				method: 'get_rfqs_count',
				args: [],
				kwargs: {context: session.user_context},
			}).then(function(result) {
				self.$el.find('#rfqs_count').html(result);
			});
		},

		get_total_purchase_order_count: function() {
			var self = this;
			self._rpc({
				model: 'purchase.order',
				method: 'get_total_purchase_order_count',
				args: [],
				kwargs: {context: session.user_context},
			}).then(function(result) {
				self.$el.find('#total_purchase_order').html(result);
			});
		},

		get_rfq_sent_count: function() {
			var self = this;
			self._rpc({
				model: 'purchase.order',
				method: 'get_rfq_sent_count',
				args: [],
				kwargs: {context: session.user_context},
			}).then(function(result) {
				self.$el.find('#rfq_sent').html(result);
			});
		},

		get_purchase_cancel_count: function() {
			var self = this;
			self._rpc({
				model: 'purchase.order',
				method: 'get_purchase_cancel_count',
				args: [],
				kwargs: {context: session.user_context},
			}).then(function(result) {
				self.$el.find('#purchase_cancel').html(result);
			});
		},

		get_vendors_lst: function() {
			var self = this;
			self._rpc({
				model: 'purchase.order',
				method: 'get_vendors_lst',
				args: [],
				kwargs: {context: session.user_context},
			}).then(function(result) {
				self.$el.find('#total_vendors').html(result);
			});
		},

		get_to_be_shipped_count: function() {
			var self = this;
			self._rpc({
				model: 'purchase.order',
				method: 'get_to_be_shipped_count',
				args: [],
				kwargs: {context: session.user_context},
			}).then(function(result) {
				self.$el.find('#to_be_shipped').html(result);
			});
		},

		get_fully_shipped_count: function() {
			var self = this;
			self._rpc({
				model: 'purchase.order',
				method: 'get_fully_shipped_count',
				args: [],
				kwargs: {context: session.user_context},
			}).then(function(result) {
				self.$el.find('#fully_shipped').html(result);
			});
		},

		get_fully_billed_count: function() {
			var self = this;
			self._rpc({
				model: 'purchase.order',
				method: 'get_fully_billed_count',
				args: [],
				kwargs: {context: session.user_context},
			}).then(function(result) {
				self.$el.find('#fully_billed').html(result);
			});
		},

		get_top_purchase_orders: function() {
			var self = this;
			self._rpc({
				model: 'purchase.order',
				method: 'get_top_purchase_orders',
				args: [],
				kwargs: {context: session.user_context},
			}).then(function(result) {
				var i;
				var body_html = "";
				for (i = 0; i < result.length; i++) {
					var data = result[i]
					body_html += "<tr class='purchase_order_details' id='"+data['po_id']+"'><td>"+data['so_number']+"</td><td>"+data['customer_name']+"</td><td>"+data['po_date']+"</td></tr>"
				}
				self.$el.find('tbody#top_four_purchase_orders').html(body_html);
			});
		},

		// GET Purchase order details record
		purchase_order_details: function(e){
		var self = this;
		var target_id = Number(e.currentTarget.id);
		this.do_action({
			name: _t("Purchase Order"),
			type: 'ir.actions.act_window',
			res_model: 'purchase.order',
			view_mode: 'form',
			views: [[false,'list'],[false, 'form']],
			domain: [['id', '=', target_id]],
			target: 'current',
			});
		},

		get_cancel_purchase_orders: function() {
			var self = this;
			self._rpc({
				model: 'purchase.order',
				method: 'get_cancel_purchase_orders',
				args: [],
				kwargs: {context: session.user_context},
			}).then(function(result) {
				var i;
				var body_html = "";
				for (i = 0; i < result.length; i++) {
					var data = result[i]
					body_html += "<tr class='purchase_order_details' id='"+data['po_id']+"'><td>"+data['so_number']+"</td><td>"+data['customer_name']+"</td><td>"+data['po_date']+"</td></tr>"
				}
				self.$el.find('tbody#cancel_purchase_orders').html(body_html);
			});
		},

		get_purchase_orders_fully_billed: function() {
			var self = this;
			self._rpc({
				model: 'purchase.order',
				method: 'get_purchase_orders_fully_billed',
				args: [],
				kwargs: {context: session.user_context},
			}).then(function(result) {
				var i;
				var body_html = "";
				for (i = 0; i < result.length; i++) {
					var data = result[i]
					body_html += "<tr class='purchase_order_details' id='"+data['po_id']+"'><td>"+data['so_number']+"</td><td>"+data['customer_name']+"</td><td>"+data['po_date']+"</td></tr>"
				}
				self.$el.find('tbody#purchase_orders_with_fully_billed').html(body_html);
			});
		},

		rfqs_info: function(e){
		var self = this;
		this.do_action({
			name: _t("Purchase Order"),
			type: 'ir.actions.act_window',
			res_model: 'purchase.order',
			view_mode: 'tree,form',
			views: [[false, 'list'],[false, 'form']],
			domain: [['state', '=','draft']],
			target: 'current',
			})
		},

		purchase_orders_info: function(e){
		var self = this;
		this.do_action({
			name: _t("Purchase Order"),
			type: 'ir.actions.act_window',
			res_model: 'purchase.order',
			view_mode: 'tree,form',
			views: [[false, 'list'],[false, 'form']],
			domain: [['state', '=','purchase']],
			target: 'current',
			})
		},

		rfq_sent_info: function(e){
		var self = this;
		this.do_action({
			name: _t("Purchase Order"),
			type: 'ir.actions.act_window',
			res_model: 'purchase.order',
			view_mode: 'tree,form',
			views: [[false, 'list'],[false, 'form']],
			domain: [['state', '=','sent']],
			target: 'current',
			})
		},

		purchase_cancel_info: function(e){
		var self = this;
		this.do_action({
			name: _t("Purchase Order"),
			type: 'ir.actions.act_window',
			res_model: 'purchase.order',
			view_mode: 'tree,form',
			views: [[false, 'list'],[false, 'form']],
			domain: [['state', '=','cancel']],
			target: 'current',
			})
		},

		vendors_info: function(e){
		var self = this;
		this.do_action({
			name: _t("Vendors"),
			type: 'ir.actions.act_window',
			res_model: 'purchase.order',
			view_mode: 'tree,form',
			views: [[false, 'list'],[false, 'form']],
			domain: [['partner_id.supplier_rank', '>=',1]],
			target: 'current',
			})
		},
		to_be_shipped: function(e){
		var self = this;
		this.do_action({
			name: _t("Purchase Order"),
			type: 'ir.actions.act_window',
			res_model: 'purchase.order',
			view_mode: 'tree,form',
			views: [[false, 'list'],[false, 'form']],
			domain: [['picking_ids.state', '=', 'assigned']],
			target: 'current',
			})
		},

		fully_shipped: function(e){
		var self = this;
		this.do_action({
			name: _t("Purchase Order"),
			type: 'ir.actions.act_window',
			res_model: 'purchase.order',
			view_mode: 'tree,form',
			views: [[false, 'list'],[false, 'form']],
			domain: [['picking_ids.state', '=', 'done']],
			target: 'current',
			})
		},

		fully_billed: function(e){
		var self = this;
		this.do_action({
			name: _t("Purchase Order"),
			type: 'ir.actions.act_window',
			res_model: 'purchase.order',
			view_mode: 'tree,form',
			views: [[false, 'list'],[false, 'form']],
			domain: [['state', '=', 'purchase'], ['invoice_status', '=', 'invoiced']],
			target: 'current',
			})
		},
	}); 
	core.action_registry.add('bv_purchase_dashboard', BVPurchaseDashboard);
	return BVPurchaseDashboard
});