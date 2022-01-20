odoo.define('bv_modern_dashboard.sale_dashboard', function (require) {
	"use strict";

	var AbstractAction = require('web.AbstractAction');
	var core = require('web.core');
	var session = require('web.session');
	var QWeb = core.qweb;
	var _t = core._t;

	var BVSaleDashboard = AbstractAction.extend({
		template: 'SaleDashboard',
		events: {
			'click .quotation-draft-info':'quotation_draft_info',
			'click .sale-order-info':'sale_order_info',
			'click .quotation-sent-info':'quotation_sent_info',
			'click .quotation-cancel-info':'quotation_cancel_info',
			'click .customers-info':'customers_info',
			'click .to-be-invoiced-info':'to_be_invoiced_info',
			'click .fully-invoiced-info':'fully_invoiced_info',
			'click .sale_order_details':'sale_order_details',
			'click .customer_details':'customer_details',
		},

		start: function() {
			var self = this;
			self.get_quotation_draft();
			self.get_sale_order_total();
			self.get_quotation_sent();
			self.get_quotation_cancel();
			self.get_customers();
			self.get_to_be_invoiced();
			self.get_fully_invoiced();
			self.get_top_orders();
			self.get_top_customers();
			self.get_sent_quotations();
			self.get_cancel_orders();
			self.price_wise_products();
			self.montly_sale_orders();
			self.quarterly_sale_orders();
			self.top_sale_team();
			self.recent_customer();
			self.recent_5_sale_order();
//			self.amount_wise_sale_order_ac_to_customer();
//			self.count_wise_customer_sale_order();
			/*self.top_2_sales_person();*/
		},

		get_quotation_draft: function() {
			var self = this;
			self._rpc({
				model: 'sale.order',
				method: 'get_quotation_draft',
				args: []
			}).then(function(result) {
				self.$el.find('#quotation_draft').html(result);
			});
		},

		get_sale_order_total: function() {
			var self = this;
			self._rpc({
				model: 'sale.order',
				method: 'get_sale_order_total',
				args: []
			}).then(function(result) {
				self.$el.find('#total_sale_order').html(result);
			});
		},

		get_quotation_sent: function() {
			var self = this;
			self._rpc({
				model: 'sale.order',
				method: 'get_quotation_sent',
				args: []
			}).then(function(result) {
				self.$el.find('#quotation_sent').html(result);
			});
		},

		get_quotation_cancel: function() {
			var self = this;
			self._rpc({
				model: 'sale.order',
				method: 'get_quotation_cancel',
				args: []
			}).then(function(result) {
				self.$el.find('#quotation_cancel').html(result);
			});
		},

		get_customers: function() {
			var self = this;
			self._rpc({
				model: 'sale.order',
				method: 'get_customers',
				args: []
			}).then(function(result) {
				self.$el.find('#total_customers').html(result);
			});
		},

		get_to_be_invoiced: function() {
			var self = this;
			self._rpc({
				model: 'sale.order',
				method: 'get_to_be_invoiced',
				args: []
			}).then(function(result) {
				self.$el.find('#to_be_invoiced').html(result);
			});
		},

		get_fully_invoiced: function() {
			var self = this;
			self._rpc({
				model: 'sale.order',
				method: 'get_fully_invoiced',
				args: []
			}).then(function(result) {
				self.$el.find('#fully_invoiced').html(result);
			});
		},

		quotation_draft_info: function(e){
		var self = this;
		var uid = session.user_context.uid;
		var user_id_domain = "";
		if (session.is_admin === true){
		    user_id_domain = [['state', '=','draft']]
        }else{
            user_id_domain = [['user_id', '=', uid], ['state', '=','draft']]
        }

		this.do_action({
			name: _t("Sale Order"),
			type: 'ir.actions.act_window',
			res_model: 'sale.order',
			view_mode: 'tree,form',
			views: [[false, 'list'],[false, 'form']],
			domain: user_id_domain,
			target: 'current',
			})
		},

		sale_order_info: function(e){
		var self = this;

		var uid = session.user_context.uid;
		var user_id_domain = "";
		if (session.is_admin === true){
		    user_id_domain = [['state', '=','sale']]
        }else{
            user_id_domain = [['user_id', '=', uid], ['state', '=','sale']]
        }

		this.do_action({
			name: _t("Sale Order"),
			type: 'ir.actions.act_window',
			res_model: 'sale.order',
			view_mode: 'tree,form',
			views: [[false, 'list'],[false, 'form']],
			domain: user_id_domain,
			target: 'current',
			})
		},

		quotation_sent_info: function(e){
		var self = this;

		var uid = session.user_context.uid;
		var user_id_domain = "";
		if (session.is_admin === true){
		    user_id_domain = [['state', '=','sent']]
        }else{
            user_id_domain = [['user_id', '=', uid], ['state', '=','sent']]
        }

		this.do_action({
			name: _t("Sale Order"),
			type: 'ir.actions.act_window',
			res_model: 'sale.order',
			view_mode: 'tree,form',
			views: [[false, 'list'],[false, 'form']],
			domain: user_id_domain,
			target: 'current',
			})
		},

		quotation_cancel_info: function(e){
		var self = this;

		var uid = session.user_context.uid;
		var user_id_domain = "";
		if (session.is_admin === true){
		    user_id_domain = [['state', '=','cancel']]
        }else{
            user_id_domain = [['user_id', '=', uid], ['state', '=','cancel']]
        }

		this.do_action({
			name: _t("Sale Order"),
			type: 'ir.actions.act_window',
			res_model: 'sale.order',
			view_mode: 'tree,form',
			views: [[false, 'list'],[false, 'form']],
			domain: user_id_domain,
			target: 'current',
			})
		},

		customers_info: function(e){
			var self = this;

			var uid = session.user_context.uid;
            var user_id_domain = "";
            if (session.is_admin === true){
                user_id_domain = [['sale_order_ids', '!=', false]]
            }else{
                user_id_domain = [['user_id', '=', uid], ['sale_order_ids', '!=', false]]
            }

			this.do_action({
			name: _t("Customers"),
			type: 'ir.actions.act_window',
			res_model: 'res.partner',
			view_mode: 'tree,form',
			views: [[false, 'list'],[false, 'form']],
			domain: user_id_domain,
			target: 'current',
			})
		},

		to_be_invoiced_info: function(e){
			var self = this;

            var uid = session.user_context.uid;
            var user_id_domain = "";
            if (session.is_admin === true){
                user_id_domain = [['invoice_status', '=', 'to invoice']]
            }else{
                user_id_domain = [['user_id', '=', uid], ['invoice_status', '=', 'to invoice']]
            }

			this.do_action({
			name: _t("Sale Order"),
			type: 'ir.actions.act_window',
			res_model: 'sale.order',
			view_mode: 'tree,form',
			views: [[false, 'list'],[false, 'form']],
			domain: user_id_domain,
			target: 'current',
			})
		},

		fully_invoiced_info: function(e){
			var self = this;

			var uid = session.user_context.uid;
            var user_id_domain = "";
            if (session.is_admin === true){
                user_id_domain = [['invoice_status', '=', 'invoiced']]
            }else{
                user_id_domain = [['user_id', '=', uid], ['invoice_status', '=', 'invoiced']]
            }

			this.do_action({
			name: _t("Sale Order"),
			type: 'ir.actions.act_window',
			res_model: 'sale.order',
			view_mode: 'tree,form',
			views: [[false, 'list'],[false, 'form']],
			domain: user_id_domain,
			target: 'current',
			})
		},

		get_top_orders: function() {
			var self = this;
			self._rpc({
				model: 'sale.order',
				method: 'get_top_orders',
				args: [],
				kwargs: {context: session.user_context},
				}).then(function(result) {
					var i;
					var body_html = "";
					for (i = 0; i < result.length; i++) {
						var data = result[i]
						body_html += "<tr class='sale_order_details' id='"+data['so_id']+"'><td>"+data['so_number']+"</td><td>"+data['customer_name']+"</td><td>"+data['amount_total']+"</td><td>"+data['so_date']+"</td></tr>"
				}
				self.$el.find('tbody#top-order-list').html(body_html);
			});
		},

        // GET Sale order details record
		sale_order_details: function(e){
		var self = this;
		var target_id = Number(e.currentTarget.id);

		var uid = session.user_context.uid;
        var user_id_domain = "";
        if (session.is_admin === true){
            user_id_domain = [['id', '=', target_id]]
        }else{
            user_id_domain = [['user_id', '=', uid], ['id', '=', target_id]]
        }

		this.do_action({
			name: _t("Sale Order"),
			type: 'ir.actions.act_window',
			res_model: 'sale.order',
			view_mode: 'form',
			views: [[false,'list'],[false, 'form']],
			domain: user_id_domain,
			target: 'current',
			});
		},

		get_cancel_orders: function() {
			var self = this;
			self._rpc({
				model: 'sale.order',
				method: 'get_cancel_orders',
				args: [],
				kwargs: {context: session.user_context},
				}).then(function(result) {
					var i;
					var body_html = "";
					for (i = 0; i < result.length; i++) {
						var data = result[i]
						body_html += "<tr class='sale_order_details' id='"+data['so_id']+"'><td>"+data['so_number']+"</td><td>"+data['customer_name']+"</td><td>"+data['so_date']+"</td></tr>"
				}
				self.$el.find('tbody#cancel-order-list').html(body_html);
			});
		},

		get_sent_quotations: function() {
			var self = this;
			self._rpc({
				model: 'sale.order',
				method: 'get_sent_quotations',
				args: [],
				kwargs: {context: session.user_context},
				}).then(function(result) {
					var i;
					var body_html = "";
					for (i = 0; i < result.length; i++) {
						var data = result[i]
						body_html += "<tr class='sale_order_details' id='"+data['so_id']+"'><td>"+data['so_number']+"</td><td>"+data['customer_name']+"</td><td>"+data['so_date']+"</td><td>"+data['so_del']+"</td></tr>"
				}
				self.$el.find('tbody#sent-order-list').html(body_html);
			});
		},

		get_top_customers: function() {
			var self = this;
			self._rpc({
				model: 'sale.order',
				method: 'get_top_customers',
				args: [],
				kwargs: {context: session.user_context},
				}).then(function(result) {
					var i;
					var body_html = "";
					for (i = 0; i < result.length; i++) {
						var data = result[i]
						body_html += "<tr class='customer_details' id='"+data['customer_id']+"'><td>"+data['customer_name']+"</td><td>"+data['sale_total']+"</td></tr>"
				}
				self.$el.find('tbody#top-customer').html(body_html);
			});
		},

		// GET top customer details record
		customer_details: function(e){
		var self = this;
		var target_id = Number(e.currentTarget.id);
		console.log(target_id);
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

//		count_wise_customer_sale_order: function(){
//			var self = this
//			/*var ctx = self.$("#count_wise_customer_sale_order");*/
//			var uid = session.user_context.uid
//			self._rpc({
//				model: "sale.order",
//				method: "count_wise_customer_sale_order",
//				args: [],
//				kwargs: {context: session.user_context},
//			}).then(function (result) {
//				var data = {
//					labels: result[1],
//					datasets: [
//					{
//						label: '',
//						data: result[0],
//						backgroundColor: [
//							"rgba(230, 230, 0,1)", "rgba(64, 191, 128, 1)", "rgba(182, 47, 137,1)",
//							"rgba(179, 179, 0,1)", "rgba(179, 0, 89,1)"
//						],
//						borderColor: [
//							"rgba(255, 99, 132, 0.2)", "rgba(54, 162, 235, 0.2)", "rgba(75, 192, 192, 0.2)",
//							"rgba(153, 102, 255, 0.2)", "rgba(10,20,30,0.3)"
//						],
//					borderWidth: 1,
//					borderColor: '#000'
//					},
//					]
//				};
//				//options
//				var options = {
//					responsive: true,
//					itle: {
//					display: false,
//					position: "top",
//					text: "",
//					fontSize: 18,
//					fontColor: "#111"
//					},
//					legend: {
//						display: false,
//						position: "bottom",
//						labels: {
//							fontColor: "#333",
//							fontSize: 16
//						}
//					},
//					scales: {
//						yAxes: [{
//						ticks: {
//							min: 0
//						}
//					}]
//					},
//					onClick:function(e){
//                            var activePoints = myCharts.getElementsAtEvent(e);
//                            if (activePoints.length>0){
//                                var selectedIndex = activePoints[0]._index;
//                                var target_id = result[2][selectedIndex]
//
//                                var user_id_domain = "";
//                                if (session.is_admin === true){
//                                     user_id_domain = [['partner_id', '=', target_id]]
//                                }else{
//                                     user_id_domain = [['user_id','=',uid],['partner_id', '=', target_id]]
//                                }
//
//                                self.do_action({
//                                    name: _t("Sale order"),
//                                    type: 'ir.actions.act_window',
//                                    res_model: 'sale.order',
//                                    view_mode: 'form',
//                                    views: [[false,'list'],[false, 'form']],
//                                    domain: user_id_domain,
//                                    target: 'current',
//                                });
//                            }
//					    },
//					onHover: function(event, chartElement){
//					     event.target.style.cursor = chartElement[0] ? 'pointer' : 'default';
//					},
//				};
//				var ctx = document.getElementById("count_wise_customer_sale_order");
//				var myCharts = new Chart(ctx, {
//					type: "bar",
//					data: data,
//					options: options
//					});
//
//			});
//		},

//		amount_wise_sale_order_ac_to_customer: function(){
//			var self = this
//			/*var ctx = self.$("#amount_wise_sale_order_ac_to_customer");*/
//			var uid = session.user_context.uid
//			self._rpc({
//				model: "sale.order",
//				method: "amount_wise_sale_order_ac_to_customer",
//				args: [],
//				kwargs: {context: session.user_context},
//			}).then(function (result) {
//				var data = {
//					labels: result[1],
//					datasets: [
//					{
//						label: '',
//						data: result[0],
//						backgroundColor: [
//							"rgba(204, 255, 255,1)",
//							"rgba(255, 204, 204, 1)",
//							"rgba(255, 153, 102,1)",
//							"rgba(255, 102, 102,1)",
//							"rgba(255, 204, 0, 1)"
//						],
//						borderColor: [
//							"rgba(255, 99, 132, 0.2)",
//							"rgba(54, 162, 235, 0.2)",
//							"rgba(75, 192, 192, 0.2)",
//							"rgba(153, 102, 255, 0.2)",
//							"rgba(10,20,30,0.3)"
//						],
//					borderWidth: 1,
//					borderColor: '#000'
//					},
//					]
//				};
//				//options
//				var options = {
//					responsive: true,
//					itle: {
//					display: false,
//					position: "top",
//					text: "",
//					fontSize: 18,
//					fontColor: "#111"
//					},
//					legend: {
//						display: false,
//						position: "bottom",
//						labels: {
//							fontColor: "#333",
//							fontSize: 16
//						}
//					},
//					scales: {
//						yAxes: [{
//						ticks: {
//							min: 0
//						}
//					}]
//					},
//					onClick:function(e){
//                            var activePoints = myCharts.getElementsAtEvent(e);
//                            if (activePoints.length>0){
//                                var selectedIndex = activePoints[0]._index;
//                                var target_id = result[2][selectedIndex]
//
//                                var user_id_domain = "";
//                                if (session.is_admin === true){
//                                     user_id_domain = [['partner_id', '=', target_id]]
//                                }else{
//                                     user_id_domain = [['user_id','=',uid],['partner_id', '=', target_id]]
//                                }
//
//                                self.do_action({
//                                    name: _t("Sale order"),
//                                    type: 'ir.actions.act_window',
//                                    res_model: 'sale.order',
//                                    view_mode: 'form',
//                                    views: [[false,'list'],[false, 'form']],
//                                    domain: user_id_domain,
//                                    target: 'current',
//                                });
//                            }
//					    },
//					onHover: function(event, chartElement){
//					     event.target.style.cursor = chartElement[0] ? 'pointer' : 'default';
//					},
//				};
//				var ctx = document.getElementById("amount_wise_sale_order_ac_to_customer");
//				var myCharts = new Chart(ctx, {
//					type: "bar",
//					data: data,
//					options: options
//					});
//
//			});
//		},

		price_wise_products: function(){
		var self = this
		/*var ctx = self.$("#price_wise_products");*/
		self._rpc({
			model: "sale.order",
			method: "price_wise_products",
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
						"rgba(204, 51, 0,1)",
						"rgba(153, 255, 51, 1)",
						"rgba(102, 102, 51,1)",
						"rgba(204, 255, 102,1)",
						"rgba(0,204,153,1)",
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
						"rgba(10,20,30,0.3)",
						"rgba(0, 204, 204,1)",
						"rgba(51, 153, 255, 1)",
						"rgba(102, 204, 255,1)",
						"rgba(204, 204, 255,1)",
						"rgba(204,204,255,1)"
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
			window.myCharts = new Chart(self.$("#price_wise_products"), {
				type: "bar",
				data: data,
				options: options
				});
			});
		},

		recent_customer: function(){
			var self = this
			self._rpc({
				model: "sale.order",
				method: "recent_customer",
				args: [],
				kwargs: {context: session.user_context},
			}).then(function (result) {
				var array_lst = []
				var options = {
					responsive: true
				};
				var ctx = document.getElementById("recent_customer");
				var myCharts = new Chart(ctx, {
					type: 'doughnut',
					tooltipFillColor: "rgba(51, 51, 51, 0.55)",
					data: {
						labels: result[1],
						datasets: [{
							data: result[0],
							backgroundColor: [
								'#ff6699 ', '#00ff00 ', '#ffff66', '#ff9900', '#cc9900'
							],
							hoverBackgroundColor: [
								'#ff6699 ', '#00ff00 ', '#ffff66', '#ff9900', '#cc9900'
							],
							borderWidth: 1
						}]
					},
					options: {
						responsive: true,
						onClick:function(e){
                            var activePoints = myCharts.getElementsAtEvent(e);
                            if (activePoints.length>0){
                                var selectedIndex = activePoints[0]._index;
                                var target_id = result[2][selectedIndex]
                                self.do_action({
                                    name: _t("Customer details"),
                                    type: 'ir.actions.act_window',
                                    res_model: 'res.partner',
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
					},
				});
			});
		},

		montly_sale_orders: function(){
			var self = this
			/*var ctx = self.$("#montly_sale_orders");*/
			var uid = session.user_context.uid
			var allowed_company_ids = session.user_context.allowed_company_ids;
			self._rpc({
				model: "sale.order",
				method: "montly_sale_orders",
				args: [],
				kwargs: {context: session.user_context},
			}).then(function (result) {
			    var dynamicColors = function() {
			        var colors=[];
			        if(result!=null && result.length>0){
			            for(var i=0;i<result[0].length;i++){
                            colors.push('#'+Math.floor(Math.random()*16777215).toString(16));
                        }
                    }
                    return colors;
			    }
				var data = {
					labels: result[2],
					datasets: [
					{
						label: '',
						data: result[0],
						backgroundColor: dynamicColors(),
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

                            if (result!=null && activePoints.length>0){
                                var selectedIndex = activePoints[0]._index;
                                var get_dt = result[2][selectedIndex]+"-01"

                                var start_dt = new Date(get_dt)
                                var month = start_dt.getMonth()
                                var year = start_dt.getFullYear()

                                var days_of_month = new Date(year, month+1, 0).getDate();
                                var end_dt = new Date(year, month, days_of_month+1);

                                var user_id_domain = "";
                                if (session.is_admin === true){
                                     user_id_domain = [['date_order', '>=', start_dt],['date_order', '<=', end_dt], ['company_id','in',allowed_company_ids]]
                                }else{
                                     user_id_domain = [['user_id', '=', uid],['date_order', '>=', start_dt],['date_order', '<=', end_dt], ['company_id','in',allowed_company_ids]]
                                }

                                self.do_action({
                                    name: _t("Sale order"),
                                    type: 'ir.actions.act_window',
                                    res_model: 'sale.order',
                                    view_mode: 'form',
                                    views: [[false,'list'],[false, 'form']],
                                    domain: user_id_domain,
                                    target: 'current',
                                });
                            }
					    },
					onHover: function(event, chartElement){
					     event.target.style.cursor = chartElement[0] ? 'pointer' : 'default';
					},
				};
				var ctx = document.getElementById("montly_sale_orders");
				var myCharts = new Chart(ctx, {
					type: "bar",
					data: data,
					options: options
					});
			});
		},

		quarterly_sale_orders: function(){
			var self = this
			var uid = session.user_context.uid
			self._rpc({
				model: "sale.order",
				method: "quarterly_sale_orders",
				args: [],
				kwargs: {context: session.user_context},
			}).then(function (result) {
			    var dynamicColors = function() {
			        var colors=[];
			        if(result!=null && result.length>0){
			            for(var i=0;i<result[0].length;i++){
                            colors.push('#'+Math.floor(Math.random()*16777215).toString(16));
                        }
                    }
                    return colors;
			    }
				var data = {
					labels: result[1],
					datasets: [
					{
						label: '',
						data: result[0],
						backgroundColor: dynamicColors(),
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

                            if (result!=null && activePoints.length>0){
//                                console.log(result[3])
                                var selectedIndex = activePoints[0]._index;

                                var start_month = result[2][selectedIndex];
                                var start_dt = new Date(start_month);

                                var end_month = result[3][selectedIndex];
                                var end_dt = new Date(end_month);

                                var user_id_domain = "";
                                if (session.is_admin === true){
                                     user_id_domain = [['date_order', '>=', start_dt],['date_order', '<=', end_month], ['state','in',['done','sale']]]
                                }else{
                                     user_id_domain = [['user_id', '=', uid],['date_order', '>=', start_dt],['date_order', '<=', end_month], ['state','in',['done','sale']]]
                                }

                                self.do_action({
                                    name: _t("Sale order"),
                                    type: 'ir.actions.act_window',
                                    res_model: 'sale.order',
                                    view_mode: 'form',
                                    views: [[false,'list'],[false, 'form']],
                                    domain: user_id_domain,
                                    target: 'current',
                                });
                            }
					    },
					onHover: function(event, chartElement){
					     event.target.style.cursor = chartElement[0] ? 'pointer' : 'default';
					},
				};
				var ctx = document.getElementById("quarterly_sale_orders");
				var myCharts = new Chart(ctx, {
					type: "bar",
					data: data,
					options: options
					});

			});
		},

		recent_5_sale_order: function(){
			var self = this
			self._rpc({
				model: "sale.order",
				method: "recent_5_sale_order",
				args: [],
				kwargs: {context: session.user_context},
			}).then(function (result) {
				var array_lst = []
				var options = {
					responsive: true
				};
                var ctx = document.getElementById("recent_5_sale_order");
				var myCharts = new Chart(ctx, {
					type: 'doughnut',
					tooltipFillColor: "rgba(51, 51, 51, 0.55)",
					data: {
						labels: result[1],
						datasets: [{
							data: result[0],
							backgroundColor: [
								'#99ff99 ', '#800080 ', '#ccb3ff', '#00b3b3', '#ff9933'
							],
							hoverBackgroundColor: [
								'#99ff99 ', '#800080 ', '#ccb3ff', '#00b3b3', '#ff9933'
							]
						}]
					},
					options: {
						responsive: true,
						onClick:function(e){
                            var activePoints = myCharts.getElementsAtEvent(e);
                            if (activePoints.length>0){
                                var selectedIndex = activePoints[0]._index;
                                var target_id = result[2][selectedIndex]
                                self.do_action({
                                    name: _t("Sale order"),
                                    type: 'ir.actions.act_window',
                                    res_model: 'sale.order',
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
					},
				});
			});
		},

		top_sale_team: function(){
			var self = this
			self._rpc({
				model: "sale.order",
				method: "top_sale_team",
				args: [],
				kwargs: {context: session.user_context},
			}).then(function (result) {
				var array_lst = []
				var options = {
					responsive: true
				};
				window.myCharts = new Chart($("#top_sale_team_sale"), {
					type: 'doughnut',
					tooltipFillColor: "rgba(51, 51, 51, 0.55)",
					data: {
						labels: result[1],
						datasets: [{
							data: result[0],
							backgroundColor: [
								'#993333 ', '#d9b38c ', '#666fcf', '#7c66cf', '#9c66cf'
							],
							hoverBackgroundColor: [
								'#993333 ', '#d9b38c ', '#666fcf', '#7c66cf', '#9c66cf'
							]
						}]
					},
					options: {
						responsive: true
					}
				});
			});
		},

	});
	core.action_registry.add('bv_sale_dashboard', BVSaleDashboard);
	return BVSaleDashboard
});