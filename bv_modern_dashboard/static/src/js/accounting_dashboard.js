odoo.define('bv_modern_dashboard.accounting_dashboard', function (require) {
	"use strict";
	 
	var AbstractAction = require('web.AbstractAction');
	var core = require('web.core');
	var QWeb = core.qweb;
	var session = require('web.session');
	var _t = core._t;
	var rpc = require('web.rpc');
	 
	var BVAccountingDashboard = AbstractAction.extend({
		template: 'AccountingDashboard',
		events: {
		    'click .to-be-invoiced-info':'to_be_invoiced_info',
			'click .invoice-open-info':'invoice_open_info',
			'click .to-be-billed-info':'to_be_billed_info',
			'click .bill-open-info':'bill_open_info',
			'click .invoice-cancel-info':'invoice_cancel_info',
			'click .customer-payment-info': 'invoice_customer_payment_info',
			'click .vendor-payment-info': 'invoice_vendor_payment_info',
		},  

		start: function() {
			var self = this;
			self.get_to_be_invoiced();
			self.get_invoice_open();
			self.get_to_be_billed_count();
			self.get_bill_open();
			self.get_cancel_invoice();
			self.get_customer_payment();
			self.get_vendor_payment();
			self.get_customer_invoice_paid_invoice_list();
			self.get_vendor_invoice_paid_invoice_list();
			self.get_customers_lst();
			self.get_vendors_lst();
			self.get_all_journal();
			self.renderElement();
			self.get_customer_invoices();
			self.get_supplier_invoices_graph();
			self.get_customer_payment_graph();
			self.get_cash_bank_balance_graph();
			/*self.get_journal_radar_graph();*/
			self.aged_payable();
			self.aged_receivable();
			self.get_income_expense();
		},

        get_income_expense: function () {
            rpc.query({
                model: 'account.move.line',
                method: 'get_income_expense',

            })
                .then(function (result) {
                    var income = result.income;
                    var expense = result.expense;
                    var profit = result.profit;
                    var labels = result.month;
                    window.myCharts = new Chart(document.getElementById("income_expense_graph").getContext('2d'), {
                        type: 'bar',
                        data: {
                            labels: labels,
                            datasets: [{
                                label: 'Income',
                                data: income,
                                backgroundColor: 'green',
                                borderColor: 'green',

                                borderWidth: 1,
                                type: 'bar',
                                fill: false
                            },
                                {
                                    label: 'Expense',
                                    data: expense,
                                    backgroundColor: 'red',
                                    borderColor: 'red',

                                    borderWidth: 1, 
                                    type: 'bar', 
                                    fill: false
                                },
                                {
                                    label: 'Profit/Loss',
                                    data: profit, 
                                    backgroundColor: 'orange',
                                    borderColor: 'orange',

                                    borderWidth: 1,
                                    type: 'line',
                                    fill: false
                                }
                            ]
                        },
                        options: {
                            responsive: true,
                            maintainAspectRatio: false,
                        }
                    });

                })
        },

		get_customer_invoices:function(){
			var self = this
			/*var ctx = self.$("#customer_invoice_graph");*/
			self._rpc({
				model: "account.move",
				method: "get_customer_invoices",
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
					text: "INVOICE DETAILS",
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
                            var target_id = result[3][selectedIndex]
                            self.do_action({
                                name: _t("Customer Invoice"),
                                type: 'ir.actions.act_window',
                                res_model: 'account.move',
                                view_mode: 'form',
                                views: [[false,'list'],[false, 'form']],
                                domain: [['partner_id', '=', target_id], ['move_type','=','out_invoice']],
                                target: 'current',
                            });
                        }
					},
					onHover: function(event, chartElement){
					    event.target.style.cursor = chartElement[0] ? 'pointer' : 'default';
					},
				};

				//create Chart class object
				// if (window.myCharts != undefined)
				//     window.myCharts.destroy();
				var myCharts = new Chart(self.$("#customer_invoice_graph"), {
					type: "bar",
					data: data,
					options: options
					});

			});
		},

		get_supplier_invoices_graph:function(){
			var self = this
			/*var ctx = self.$("#supplier_invoice_graph");*/
			self._rpc({
				model: "account.move",
				method: "get_supplier_invoices",
				args: [],
				kwargs: {context: session.user_context},
			}).then(function (supplier_result) {
				var data = {
					labels: supplier_result[1],
					datasets: [
					{
						label: '',
						data: supplier_result[0],
						backgroundColor: [
							"rgba(255, 99, 132,1)",
							"rgba(54, 162, 235,1)",
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
					text: "INVOICE DETAILS",
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
                            var target_id = supplier_result[3][selectedIndex]
                            self.do_action({
                                name: _t("Supplier Invoice"),
                                type: 'ir.actions.act_window',
                                res_model: 'account.move',
                                view_mode: 'form',
                                views: [[false,'list'],[false, 'form']],
                                domain: [['partner_id', '=', target_id], ['move_type','=','in_invoice']],
                                target: 'current',
                            });
                        }
					},
					onHover: function(event, chartElement){
					    event.target.style.cursor = chartElement[0] ? 'pointer' : 'default';
					},
				};

				// if (window.myCharts != undefined)
				//     window.myCharts.destroy();
				var myCharts = new Chart(self.$("#supplier_invoice_graph"), {
					type: "bar",
					data: data,
					options: options
					});
			});
		},

		get_customer_payment_graph:function(){
			var self = this
			/*var ctx = self.$("#customer_payment_graph");*/
			self._rpc({
				model: "account.payment",
				method: "get_customer_payment_graph",
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
							"rgba(253, 91, 29,1)",
							"rgba(177, 92, 74, 1)",
							"rgba(230, 92, 74, 1)",
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
					text: "INVOICE DETAILS",
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
                            var target_id = result[3][selectedIndex]
                            self.do_action({
                                name: _t("Customer Payment"),
                                type: 'ir.actions.act_window',
                                res_model: 'account.payment',
                                view_mode: 'form',
                                views: [[false,'list'],[false, 'form']],
                                domain: [['partner_id', '=', target_id]],
                                target: 'current',
                            });
                        }
					},
					onHover: function(event, chartElement){
					    event.target.style.cursor = chartElement[0] ? 'pointer' : 'default';
					},
				};

				//create Chart class object
				// if (window.myCharts != undefined)
				//     window.myCharts.destroy();
				var myCharts = new Chart(self.$("#customer_payment_graph"), {
					type: "bar",
					data: data,
					options: options
					});

			});
		},

		get_cash_bank_balance_graph:function(){
			var self = this
			/*var ctx = self.$("#cash_bank_balance_graph");*/
			self._rpc({
				model: "account.move.line",
				method: "get_cash_bank_balance_graph",
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
							"rgba(230, 210, 74, 1)",
							"rgba(230, 255, 234, 1)",
							"rgba(255, 220, 166, 1)",
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
					text: "INVOICE DETAILS",
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
                            var target_id = result[3][selectedIndex]
                            self.do_action({
                                name: _t("Cash and Bank Balance"),
                                type: 'ir.actions.act_window',
                                res_model: 'account.move.line',
                                view_mode: 'form',
                                views: [[false,'list'],[false, 'form']],
                                domain: [['partner_id', '=', target_id]],
                                target: 'current',
                            });
                        }
					},
					onHover: function(event, chartElement){
					    event.target.style.cursor = chartElement[0] ? 'pointer' : 'default';
					},
				};

				//create Chart class object
				// if (window.myCharts != undefined)
				//     window.myCharts.destroy();
				var myCharts = new Chart(self.$("#cash_bank_balance_graph"), {
					type: "bar",
					data: data,
					options: options
					});

			});
		},

		renderElement: function (ev) {
			var self = this;
			$.when(this._super())
			.then(function (ev) {
				self._rpc({
					model: "account.move",
					method: "get_customer_data_for_chart",
					args: [],
					kwargs: {context: session.user_context},
				}).then(function (result) {
					$(document).ready(function () {
						var options = {
							responsive: true
						};
						var myCharts = new Chart($("#canvas1"), {
							type: 'doughnut',
							tooltipFillColor: "rgba(51, 51, 51, 0.55)",
							data: {
								labels: result[1],
								datasets: [{
									data: result[0],
									backgroundColor: [
										'#cc3300 ', '#b38600 ', '#ff0066', '#660033', '#9c66cf'
									],
									hoverBackgroundColor: [
										'#cc3300 ', '#b38600 ', '#ff0066', '#660033', '#9c66cf'
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
							}
						});
					});
				})
			});
		},

		aged_payable: function(){
			var self = this
			self._rpc({
				model: "account.move",
				method: "get_age_payable",
				args: [],
				kwargs: {context: session.user_context},
			}).then(function (result) {
				var array_lst = []
				var options = {
					responsive: true
				};
				window.myCharts = new Chart($("#agedPayable"), {
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
						responsive: true
					}
				});
			});
		},

		aged_receivable: function(){
			var self = this
			self._rpc({
				model: "account.move",
				method: "get_age_receivable",
				args: [],
				kwargs: {context: session.user_context},
			}).then(function (result) {
				var array_lst = []
				var options = {
					responsive: true
				};
				window.myCharts = new Chart($("#agedReceivable"), {
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
							]
						}]
					},
					options: {
						responsive: true
					}
				});
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

		get_invoice_open: function() {
			var self = this;
			self._rpc({
				model: 'account.move',
				method: 'get_invoice_open',
				args: [],
				kwargs: {context: session.user_context},
			}).then(function(result) {
				self.$el.find('#open_invoice').html(result);
			});
		},

        get_to_be_billed_count: function() {
			var self = this;
			self._rpc({
				model: 'purchase.order',
				method: 'get_to_be_billed_count',
				args: []
			}).then(function(result) {
				self.$el.find('#to_be_billed').html(result);
			});
		},

		get_bill_open: function() {
			var self = this;
			self._rpc({
				model: 'account.move',
				method: 'get_bill_open',
				args: [],
				kwargs: {context: session.user_context},
			}).then(function(result) {
				self.$el.find('#open_bill').html(result);
			});
		},

		get_cancel_invoice: function() {
			var self = this;
			self._rpc({
				model: 'account.move',
				method: 'get_invoice_cancel',
				args: [],
				kwargs: {context: session.user_context},
			}).then(function(result) {
				self.$el.find('#cancel_invoices').html(result);
			});
		},

		get_customer_payment: function() {
			var self = this;
			self._rpc({
				model: 'account.payment',
				method: 'get_customer_payment',
				args: [],
				kwargs: {context: session.user_context},
			}).then(function(result) {
				self.$el.find('#Customer_payment').html(result);
			});
		},

		get_vendor_payment: function() {
			var self = this;
			self._rpc({
				model: 'account.payment',
				method: 'get_vendor_payment',
				args: [],
				kwargs: {context: session.user_context},
			}).then(function(result) {
				self.$el.find('#vendor_payment').html(result);
			});
		},

		get_customer_invoice_paid_invoice_list: function() {
			var self = this;
			self._rpc({
				model: 'account.move',
				method: 'get_customer_invoice_paid_invoice_list',
				args: [],
				kwargs: {context: session.user_context},
			}).then(function(result) {
				var i;
				var body_html = "";
				for (i = 0; i < result.length; i++) {
					var data = result[i]
					body_html += "<tr><td>"+data['move_number']+"</td><td>"+data['partner_name']+"</td><td>"+data['move_total']+"</td></tr>"
				}
				self.$el.find('tbody#customer_payment_lst').html(body_html);
			});
		},

		get_vendor_invoice_paid_invoice_list: function() {
			var self = this;
			self._rpc({
				model: 'account.move',
				method: 'get_vendor_invoice_paid_invoice_list',
				args: [],
				kwargs: {context: session.user_context},
			}).then(function(result) {
				var i;
				var body_html = "";
				for (i = 0; i < result.length; i++) {
					var data = result[i]
					body_html += "<tr><td>"+data['move_number']+"</td><td>"+data['partner_name']+"</td><td>"+data['move_total']+"</td></tr>"
				}
				self.$el.find('tbody#vendor_payment_lst').html(body_html);
			});
		},

		get_customers_lst: function() {
			var self = this;
			self._rpc({
				model: 'account.move',
				method: 'get_customers_lst',
				args: [],
				kwargs: {context: session.user_context},
			}).then(function(result) {
				var i;
				var body_html = "";
				for (i = 0; i < result.length; i++) {
					var data = result[i]
					body_html += "<tr><td>"+data['partner_name']+"</td></tr>"
				}
				self.$el.find('tbody#customer_lst').html(body_html);
			});
		},

		get_vendors_lst: function() {
			var self = this;
			self._rpc({
				model: 'account.move',
				method: 'get_vendors_lst',
				args: [],
				kwargs: {context: session.user_context},
			}).then(function(result) {
				var i;
				var body_html = "";
				for (i = 0; i < result.length; i++) {
					var data = result[i]
					body_html += "<tr><td>"+data['vendor_name']+"</td></tr>"
				}
				self.$el.find('tbody#vendor_lst').html(body_html);
			});
		},

		get_all_journal: function() {
			var self = this;
			self._rpc({
				model: 'account.journal',
				method: 'get_all_journals',
				args: [],
				kwargs: {context: session.user_context},
			}).then(function(result) {
				var i;
				var body_html = "";
				for (i = 0; i < result.length; i++) {
					var data = result[i]
					body_html += "<tr><td>"+data['journal_name']+"</td><td>"+data['journal_type']+"</td></tr>"
				}
				self.$el.find('tbody#journal_lst').html(body_html);
			});
		},


        to_be_invoiced_info: function(e){
			var self = this;
            var uid = session.user_context.uid;
            var user_id_domain = "";
            if (session.is_admin === true){
                user_id_domain = [['invoice_status', '=', 'to invoice']]
            }else{
                user_id_domain = [['invoice_status', '=', 'to invoice']]
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


		to_be_billed_info: function(e){
			var self = this;
            var uid = session.user_context.uid;
            var user_id_domain = "";
            if (session.is_admin === true){
                user_id_domain = [['invoice_status', '=', 'to invoice']]
            }else{
                user_id_domain = [['invoice_status', '=', 'to invoice']]
            }

			this.do_action({
			name: _t("Purchase Order"),
			type: 'ir.actions.act_window',
			res_model: 'purchase.order',
			view_mode: 'tree,form',
			views: [[false, 'list'],[false, 'form']],
			domain: user_id_domain,
			target: 'current',
			})
		},


		invoice_open_info: function(e){
		var self = this;
		this.do_action({
			name: _t("Account Move"),
			type: 'ir.actions.act_window',
			res_model: 'account.move',
			view_mode: 'tree,form',
			views: [[false, 'list'],[false, 'form']],
			domain: [['payment_state', '=','not_paid'], ['state', '=', 'posted'],['move_type', '=', 'out_invoice']],
			target: 'current',
			})
		},

		bill_open_info: function(e){
		var self = this;
		this.do_action({
			name: _t("Account Move"),
			type: 'ir.actions.act_window',
			res_model: 'account.move',
			view_mode: 'tree,form',
			views: [[false, 'list'],[false, 'form']],
			domain: [['payment_state', '=','not_paid'], ['state', '=', 'posted'],['move_type', '=', 'in_invoice']],
			target: 'current',
			})
		},

		invoice_cancel_info: function(e){
		var self = this;
		this.do_action({
			name: _t("Account Move"),
			type: 'ir.actions.act_window',
			res_model: 'account.move',
			view_mode: 'tree,form',
			views: [[false, 'list'],[false, 'form']],
			domain: [['state', '=','cancel']],
			target: 'current',
			})
		},

		invoice_customer_payment_info:function(e){
		var self = this;
		this.do_action({
			name: _t("Customer Payment"),
			type: 'ir.actions.act_window',
			res_model: 'account.payment',
			view_mode: 'tree,form',
			views: [[false, 'list'],[false, 'form']],
			domain: [['partner_type', '=','customer']],
			target: 'current',
			})
		},  

		invoice_vendor_payment_info:function(e){
		var self = this;
		this.do_action({
			name: _t("Vendor Payment"),
			type: 'ir.actions.act_window',
			res_model: 'account.payment',
			view_mode: 'tree,form',
			views: [[false, 'list'],[false, 'form']],
			domain: [['partner_type', '=','supplier']],
			target: 'current',
			})
		},
	}); 
	core.action_registry.add('bv_accounting_dashboard', BVAccountingDashboard);
	return BVAccountingDashboard
});