import 'package:flutter/material.dart';
import '../../../core/theme/app_theme.dart';
import '../../../core/utils/currency_formatter.dart';
import '../../home/presentation/screens/home_screen.dart';
import '../../payment_intent/presentation/screens/payment_intent_screen.dart';
import '../../ai_assistant/presentation/screens/ai_assistant_screen.dart';
import '../../transactions/presentation/screens/add_transaction_screen.dart';

// --- Placeholder/Mock Screens for complete navigation ---
class TransactionsScreen extends StatelessWidget {
  const TransactionsScreen({super.key});
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Transaction Ledger')),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          _txCard('College Fees', 'Engineering College', -5000.0, 'Education', '7 days ago'),
          _txCard('Monthly Salary', 'Tech Solutions Ltd', 35000.0, 'Salary', '9 days ago'),
          _txCard('Dinner with friends', 'Swiggy', -850.0, 'Food', '4 days ago'),
          _txCard('Uber Ride', 'Uber India', -450.0, 'Transportation', '3 days ago'),
          _txCard('Amazon Refund', 'Amazon', 1000.0, 'Shopping', '12 hours ago'),
        ],
      ),
    );
  }

  Widget _txCard(String title, String merchant, double amount, String category, String time) {
    final isDebit = amount < 0;
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: ListTile(
        leading: CircleAvatar(
          backgroundColor: isDebit ? Colors.red.withOpacity(0.1) : Colors.green.withOpacity(0.1),
          child: Icon(isDebit ? Icons.arrow_outward : Icons.arrow_downward, color: isDebit ? Colors.red : Colors.green),
        ),
        title: Text(title, style: const TextStyle(fontWeight: FontWeight.bold)),
        subtitle: Text(' •  • ', style: const TextStyle(fontSize: 12, color: Colors.grey)),
        trailing: Text(
          CurrencyFormatter.formatINR(amount.abs()),
          style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16, color: isDebit ? Colors.red : Colors.green),
        ),
      ),
    );
  }
}

class AnalyticsScreen extends StatelessWidget {
  const AnalyticsScreen({super.key});
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Financial Analytics & Insights')),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text('Monthly Spending Breakdown', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
                  const SizedBox(height: 16),
                  _barProgress('Education', 0.50, '₹5,000 / ₹10,000', Colors.blue),
                  _barProgress('Food', 0.76, '₹3,800 / ₹5,000', Colors.orange),
                  _barProgress('Transportation', 0.40, '₹1,200 / ₹3,000', Colors.teal),
                ],
              ),
            ),
          ),
          const SizedBox(height: 16),
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text('Top Payment Methods', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
                  const SizedBox(height: 12),
                  _methodRow('UPI (Google Pay / PhonePe)', '72%'),
                  _methodRow('Bank Transfer (NEFT/IMPS)', '20%'),
                  _methodRow('Cash', '8%'),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _barProgress(String label, double value, String amount, Color color) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [Text(label), Text(amount, style: const TextStyle(fontWeight: FontWeight.bold))],
          ),
          const SizedBox(height: 6),
          LinearProgressIndicator(value: value, color: color, backgroundColor: Colors.grey.shade200, minHeight: 8),
        ],
      ),
    );
  }

  Widget _methodRow(String method, String pct) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [Text(method), Text(pct, style: const TextStyle(fontWeight: FontWeight.bold))],
      ),
    );
  }
}

class ProfileScreen extends StatelessWidget {
  const ProfileScreen({super.key});
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Profile & Security')),
      body: ListView(
        children: [
          const UserAccountsDrawerHeader(
            accountName: Text('Siva', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 18)),
            accountEmail: Text('siva@moneyflow.ai'),
            currentAccountPicture: CircleAvatar(backgroundColor: Colors.white, child: Text('S', style: TextStyle(fontSize: 24, color: AppColors.primary))),
            decoration: BoxDecoration(color: AppColors.primary),
          ),
          ListTile(leading: const Icon(Icons.shield_outlined), title: const Text('Security & Biometrics'), trailing: const Icon(Icons.chevron_right), onTap: () {}),
          ListTile(leading: const Icon(Icons.lock_outline), title: const Text('App PIN'), trailing: const Icon(Icons.chevron_right), onTap: () {}),
          ListTile(leading: const Icon(Icons.account_balance_outlined), title: const Text('Manage Accounts'), trailing: const Icon(Icons.chevron_right), onTap: () {}),
          ListTile(leading: const Icon(Icons.file_download_outlined), title: const Text('Export Financial Records (CSV/PDF)'), trailing: const Icon(Icons.chevron_right), onTap: () {}),
          ListTile(leading: const Icon(Icons.cloud_sync_outlined), title: const Text('Backup & Restore'), trailing: const Icon(Icons.chevron_right), onTap: () {}),
          ListTile(leading: const Icon(Icons.privacy_tip_outlined), title: const Text('Privacy & Consent Settings'), trailing: const Icon(Icons.chevron_right), onTap: () {}),
          const Divider(),
          ListTile(leading: const Icon(Icons.logout, color: Colors.red), title: const Text('Sign Out', style: TextStyle(color: Colors.red)), onTap: () {}),
        ],
      ),
    );
  }
}

// --- Main Navigation Container ---
class MainNavigationScreen extends StatefulWidget {
  const MainNavigationScreen({super.key});

  @override
  State<MainNavigationScreen> createState() => _MainNavigationScreenState();
}

class _MainNavigationScreenState extends State<MainNavigationScreen> {
  int _currentIndex = 0;

  final List<Widget> _screens = const [
    HomeScreen(),
    TransactionsScreen(),
    PaymentIntentScreen(),
    AnalyticsScreen(),
    ProfileScreen(),
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: _screens[_currentIndex],
      floatingActionButton: FloatingActionButton(
        backgroundColor: AppColors.primary,
        onPressed: () {
          Navigator.push(
            context,
            MaterialPageRoute(builder: (_) => const AddTransactionScreen(type: 'DEBIT')),
          );
        },
        child: const Icon(Icons.add, color: Colors.white),
      ),
      bottomNavigationBar: NavigationBar(
        selectedIndex: _currentIndex,
        onDestinationSelected: (idx) => setState(() => _currentIndex = idx),
        destinations: const [
          NavigationDestination(icon: Icon(Icons.home_outlined), selectedIcon: Icon(Icons.home), label: 'Home'),
          NavigationDestination(icon: Icon(Icons.receipt_long_outlined), selectedIcon: Icon(Icons.receipt_long), label: 'Transactions'),
          NavigationDestination(icon: Icon(Icons.payment_outlined), selectedIcon: Icon(Icons.payment), label: 'Pay'),
          NavigationDestination(icon: Icon(Icons.bar_chart_outlined), selectedIcon: Icon(Icons.bar_chart), label: 'Analytics'),
          NavigationDestination(icon: Icon(Icons.person_outline), selectedIcon: Icon(Icons.person), label: 'Profile'),
        ],
      ),
    );
  }
}
