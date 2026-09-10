import 'package:flutter/material.dart';
import '../../../core/theme/app_theme.dart';
import '../../../core/utils/currency_formatter.dart';

class TransferScreen extends StatefulWidget {
  const TransferScreen({super.key});

  @override
  State<TransferScreen> createState() => _TransferScreenState();
}

class _TransferScreenState extends State<TransferScreen> {
  final _amountController = TextEditingController();
  final _purposeController = TextEditingController(text: 'Account Fund Transfer');
  String _fromAccount = 'SBI Savings (₹22,000)';
  String _toAccount = 'HDFC Salary (₹12,500)';

  final List<String> _accounts = [
    'SBI Savings (₹22,000)',
    'HDFC Salary (₹12,500)',
    'Cash Wallet (₹3,000)',
    'Paytm Wallet (₹2,000)'
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Account Transfer')),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Transfers between your own accounts do NOT increase or decrease total wealth.',
              style: TextStyle(color: Colors.grey, fontSize: 13),
            ),
            const SizedBox(height: 20),

            const Text('From Account', style: TextStyle(fontWeight: FontWeight.bold)),
            const SizedBox(height: 8),
            DropdownButtonFormField<String>(
              value: _fromAccount,
              items: _accounts.map((a) => DropdownMenuItem(value: a, child: Text(a))).toList(),
              onChanged: (v) => setState(() => _fromAccount = v!),
              decoration: const InputDecoration(border: OutlineInputBorder(borderRadius: BorderRadius.all(Radius.circular(12)))),
            ),
            const SizedBox(height: 16),

            const Center(child: Icon(Icons.arrow_downward_rounded, color: AppColors.primary, size: 28)),
            const SizedBox(height: 16),

            const Text('To Account', style: TextStyle(fontWeight: FontWeight.bold)),
            const SizedBox(height: 8),
            DropdownButtonFormField<String>(
              value: _toAccount,
              items: _accounts.map((a) => DropdownMenuItem(value: a, child: Text(a))).toList(),
              onChanged: (v) => setState(() => _toAccount = v!),
              decoration: const InputDecoration(border: OutlineInputBorder(borderRadius: BorderRadius.all(Radius.circular(12)))),
            ),
            const SizedBox(height: 20),

            const Text('Amount', style: TextStyle(fontWeight: FontWeight.bold)),
            const SizedBox(height: 8),
            TextField(
              controller: _amountController,
              keyboardType: TextInputType.number,
              style: const TextStyle(fontSize: 26, fontWeight: FontWeight.bold, color: AppColors.primary),
              decoration: const InputDecoration(
                prefixText: '₹ ',
                hintText: '0.00',
                border: OutlineInputBorder(borderRadius: BorderRadius.all(Radius.circular(12))),
              ),
            ),
            const SizedBox(height: 28),

            SizedBox(
              width: double.infinity,
              height: 52,
              child: ElevatedButton(
                onPressed: () {
                  final amt = double.tryParse(_amountController.text) ?? 0.0;
                  if (amt <= 0 || _fromAccount == _toAccount) {
                    ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(content: Text('Please select different accounts and valid amount')),
                    );
                    return;
                  }
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(content: Text('Transferred  successfully!')),
                  );
                  Navigator.pop(context);
                },
                child: const Text('Execute Transfer'),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
