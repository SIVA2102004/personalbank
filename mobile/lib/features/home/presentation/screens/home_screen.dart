import 'package:flutter/material.dart';
import '../../../core/theme/app_theme.dart';
import '../../../core/utils/currency_formatter.dart';
import '../../payment_intent/presentation/screens/payment_intent_screen.dart';
import '../../transactions/presentation/screens/add_transaction_screen.dart';
import '../../voice/presentation/screens/voice_entry_screen.dart';
import '../../receipts/presentation/screens/receipt_scanner_screen.dart';
import '../../transactions/presentation/screens/transfer_screen.dart';
import '../../../services/api_service.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  Map<String, dynamic>? _data;
  bool _loading = true;

  @override
  void initState() {
    super.initState();
    _loadDashboard();
  }

  Future<void> _loadDashboard() async {
    final res = await apiService.getDashboard();
    if (mounted) {
      setState(() {
        _data = res;
        _loading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_loading) {
      return const Center(child: CircularProgressIndicator());
    }

    final double totalBalance = (_data?['total_balance'] as num?)?.toDouble() ?? 47500.0;
    final double income = (_data?['month_income'] as num?)?.toDouble() ?? 35000.0;
    final double expense = (_data?['month_expense'] as num?)?.toDouble() ?? 18500.0;
    final double remaining = (_data?['remaining'] as num?)?.toDouble() ?? 16500.0;
    final List accounts = _data?['accounts'] ?? [];
    final List recentTxs = _data?['recent_transactions'] ?? [];

    return Scaffold(
      appBar: AppBar(
        title: const Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Good evening, Siva 👋', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
            Text('MoneyFlow AI Assistant Active', style: TextStyle(fontSize: 12, color: Colors.grey)),
          ],
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.notifications_none_outlined),
            onPressed: () {},
          ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: _loadDashboard,
        child: SingleChildScrollView(
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Total Balance Hero Card
              Container(
                width: double.infinity,
                padding: const EdgeInsets.all(20),
                decoration: BoxDecoration(
                  gradient: const LinearGradient(
                    colors: [Color(0xFF1E3A8A), Color(0xFF3B82F6)],
                    begin: Alignment.topLeft,
                    end: Alignment.bottomRight,
                  ),
                  borderRadius: BorderRadius.circular(20),
                  boxShadow: [
                    BoxShadow(
                      color: const Color(0xFF1E3A8A).withOpacity(0.3),
                      blurRadius: 12,
                      offset: const Offset(0, 6),
                    ),
                  ],
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text('Total Money Across Accounts', style: TextStyle(color: Colors.white70, fontSize: 13)),
                    const SizedBox(height: 6),
                    Text(
                      CurrencyFormatter.formatINR(totalBalance),
                      style: const TextStyle(color: Colors.white, fontSize: 32, fontWeight: FontWeight.bold),
                    ),
                    const SizedBox(height: 16),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        _summaryItem('Income', '+', Colors.emeraldAccent, Icons.arrow_downward),
                        _summaryItem('Expenses', '-', Colors.redAccent, Icons.arrow_upward),
                        _summaryItem('Remaining', CurrencyFormatter.formatINR(remaining), Colors.cyanAccent, Icons.savings_outlined),
                      ],
                    ),
                  ],
                ),
              ),

              const SizedBox(height: 20),

              // Quick Actions
              const Text('Quick Actions', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
              const SizedBox(height: 12),
              SingleChildScrollView(
                scrollDirection: Axis.horizontal,
                child: Row(
                  children: [
                    _quickActionButton(
                      'Pay Now', Icons.send_rounded, AppColors.primary,
                      () => Navigator.push(context, MaterialPageRoute(builder: (_) => const PaymentIntentScreen())),
                    ),
                    _quickActionButton(
                      'Expense', Icons.remove_circle_outline, AppColors.expense,
                      () => Navigator.push(context, MaterialPageRoute(builder: (_) => const AddTransactionScreen(type: 'DEBIT'))),
                    ),
                    _quickActionButton(
                      'Income', Icons.add_circle_outline, AppColors.accent,
                      () => Navigator.push(context, MaterialPageRoute(builder: (_) => const AddTransactionScreen(type: 'CREDIT'))),
                    ),
                    _quickActionButton(
                      'Transfer', Icons.swap_horiz_rounded, Colors.purple,
                      () => Navigator.push(context, MaterialPageRoute(builder: (_) => const TransferScreen())),
                    ),
                    _quickActionButton(
                      'Voice', Icons.mic_none_rounded, Colors.teal,
                      () => Navigator.push(context, MaterialPageRoute(builder: (_) => const VoiceEntryScreen())),
                    ),
                    _quickActionButton(
                      'Scan', Icons.receipt_long_rounded, Colors.indigo,
                      () => Navigator.push(context, MaterialPageRoute(builder: (_) => const ReceiptScannerScreen())),
                    ),
                  ],
                ),
              ),

              const SizedBox(height: 24),

              // Accounts Horizontal List
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  const Text('Your Financial Accounts', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
                  TextButton(onPressed: () {}, child: const Text('View All')),
                ],
              ),
              const SizedBox(height: 8),
              SizedBox(
                height: 110,
                child: ListView.separated(
                  scrollDirection: Axis.horizontal,
                  itemCount: accounts.length,
                  separatorBuilder: (_, __) => const SizedBox(width: 12),
                  itemBuilder: (context, i) {
                    final acc = accounts[i];
                    return Container(
                      width: 150,
                      padding: const EdgeInsets.all(14),
                      decoration: BoxDecoration(
                        color: Theme.of(context).cardTheme.color,
                        borderRadius: BorderRadius.circular(16),
                        border: Border.all(color: Colors.grey.withOpacity(0.2)),
                      ),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Row(
                            children: [
                              CircleAvatar(
                                radius: 10,
                                backgroundColor: Color(int.parse(acc['color'].toString().replaceAll('#', '0xFF'))),
                              ),
                              const SizedBox(width: 6),
                              Expanded(
                                child: Text(
                                  acc['name'],
                                  style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 13),
                                  overflow: TextOverflow.ellipsis,
                                ),
                              ),
                            ],
                          ),
                          Text(
                            CurrencyFormatter.formatINR((acc['balance'] as num).toDouble()),
                            style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                          ),
                        ],
                      ),
                    );
                  },
                ),
              ),

              const SizedBox(height: 24),

              // AI Financial Insight Banner
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: Colors.blue.withOpacity(0.08),
                  borderRadius: BorderRadius.circular(16),
                  border: Border.all(color: Colors.blue.withOpacity(0.2)),
                ),
                child: const Row(
                  children: [
                    Icon(Icons.auto_awesome, color: Colors.blueAccent, size: 28),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text('AI Spending Insight', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 14)),
                          SizedBox(height: 2),
                          Text('Your food spending is 18% lower than last month. You have ₹1,200 remaining in your Food Budget.', style: TextStyle(fontSize: 13)),
                        ],
                      ),
                    ),
                  ],
                ),
              ),

              const SizedBox(height: 24),

              // Recent Transactions
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  const Text('Recent Transactions', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
                  TextButton(onPressed: () {}, child: const Text('See All')),
                ],
              ),
              const SizedBox(height: 8),
              ListView.separated(
                physics: const NeverScrollableScrollPhysics(),
                shrinkWrap: true,
                itemCount: recentTxs.length,
                separatorBuilder: (_, __) => const Divider(height: 1),
                itemBuilder: (context, idx) {
                  final tx = recentTxs[idx];
                  final isDebit = tx['type'] == 'DEBIT';
                  return ListTile(
                    contentPadding: EdgeInsets.zero,
                    leading: CircleAvatar(
                      backgroundColor: isDebit ? Colors.red.withOpacity(0.1) : Colors.green.withOpacity(0.1),
                      child: Icon(
                        isDebit ? Icons.arrow_outward_rounded : Icons.arrow_downward_rounded,
                        color: isDebit ? Colors.red : Colors.green,
                        size: 20,
                      ),
                    ),
                    title: Text(tx['purpose'], style: const TextStyle(fontWeight: FontWeight.w600)),
                    subtitle: Text(tx['date'], style: const TextStyle(fontSize: 12, color: Colors.grey)),
                    trailing: Text(
                      '',
                      style: TextStyle(
                        fontWeight: FontWeight.bold,
                        fontSize: 15,
                        color: isDebit ? Colors.red : Colors.green,
                      ),
                    ),
                  );
                },
              ),
              const SizedBox(height: 30),
            ],
          ),
        ),
      ),
    );
  }

  Widget _summaryItem(String label, String value, Color color, IconData icon) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Icon(icon, size: 12, color: color),
            const SizedBox(width: 4),
            Text(label, style: const TextStyle(color: Colors.white70, fontSize: 11)),
          ],
        ),
        const SizedBox(height: 2),
        Text(value, style: TextStyle(color: color, fontWeight: FontWeight.bold, fontSize: 13)),
      ],
    );
  }

  Widget _quickActionButton(String label, IconData icon, Color color, VoidCallback onTap) {
    return Padding(
      padding: const EdgeInsets.only(right: 12),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(16),
        child: Container(
          width: 78,
          padding: const EdgeInsets.symmetric(vertical: 12),
          decoration: BoxDecoration(
            color: color.withOpacity(0.1),
            borderRadius: BorderRadius.circular(16),
            border: Border.all(color: color.withOpacity(0.2)),
          ),
          child: Column(
            children: [
              Icon(icon, color: color, size: 24),
              const SizedBox(height: 6),
              Text(label, style: TextStyle(fontSize: 11, fontWeight: FontWeight.w600, color: color)),
            ],
          ),
        ),
      ),
    );
  }
}
