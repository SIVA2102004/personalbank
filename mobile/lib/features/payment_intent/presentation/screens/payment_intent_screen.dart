import 'package:flutter/material.dart';
import '../../../core/theme/app_theme.dart';
import '../../../core/utils/currency_formatter.dart';

class PaymentIntentScreen extends StatefulWidget {
  const PaymentIntentScreen({super.key});

  @override
  State<PaymentIntentScreen> createState() => _PaymentIntentScreenState();
}

class _PaymentIntentScreenState extends State<PaymentIntentScreen> {
  final _amountController = TextEditingController();
  final _purposeController = TextEditingController();
  final _vpaController = TextEditingController();
  String _selectedAccount = 'SBI Savings (₹22,000)';
  String _selectedMethod = 'UPI';

  final List<String> _accounts = [
    'SBI Savings (₹22,000)',
    'HDFC Salary (₹12,500)',
    'Cash Wallet (₹3,000)',
    'Paytm Wallet (₹2,000)'
  ];

  final List<String> _methods = ['UPI', 'Bank transfer', 'Card', 'Cash'];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Create Payment Intent')),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text('What do you want to pay?', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
            const SizedBox(height: 8),
            TextField(
              controller: _amountController,
              keyboardType: TextInputType.number,
              style: const TextStyle(fontSize: 28, fontWeight: FontWeight.bold, color: AppColors.primary),
              decoration: const InputDecoration(
                prefixText: '₹ ',
                hintText: '0.00',
                border: OutlineInputBorder(borderRadius: BorderRadius.all(Radius.circular(12))),
              ),
            ),
            const SizedBox(height: 20),

            const Text('Payment Purpose (Required)', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
            const SizedBox(height: 8),
            TextField(
              controller: _purposeController,
              decoration: const InputDecoration(
                hintText: 'e.g. College books, Dinner with friends, Uber',
                border: OutlineInputBorder(borderRadius: BorderRadius.all(Radius.circular(12))),
              ),
            ),
            const SizedBox(height: 20),

            const Text('Choose Account', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
            const SizedBox(height: 8),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 16),
              decoration: BoxDecoration(
                border: Border.all(color: Colors.grey.shade400),
                borderRadius: BorderRadius.circular(12),
              ),
              child: DropdownButtonHideUnderline(
                child: DropdownButton<String>(
                  isExpanded: true,
                  value: _selectedAccount,
                  items: _accounts.map((e) => DropdownMenuItem(value: e, child: Text(e))).toList(),
                  onChanged: (v) => setState(() => _selectedAccount = v!),
                ),
              ),
            ),
            const SizedBox(height: 20),

            const Text('Choose Payment Method', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
            const SizedBox(height: 8),
            Wrap(
              spacing: 10,
              children: _methods.map((m) {
                final isSelected = _selectedMethod == m;
                return ChoiceChip(
                  label: Text(m),
                  selected: isSelected,
                  selectedColor: AppColors.primaryLight,
                  labelStyle: TextStyle(color: isSelected ? Colors.white : Colors.black87),
                  onSelected: (_) => setState(() => _selectedMethod = m),
                );
              }).toList(),
            ),
            const SizedBox(height: 20),

            if (_selectedMethod == 'UPI') ...[
              const Text('Payee UPI ID (Optional)', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
              const SizedBox(height: 8),
              TextField(
                controller: _vpaController,
                decoration: const InputDecoration(
                  hintText: 'merchant@upi or friend@oksbi',
                  border: OutlineInputBorder(borderRadius: BorderRadius.all(Radius.circular(12))),
                ),
              ),
              const SizedBox(height: 20),
            ],

            const SizedBox(height: 24),
            SizedBox(
              width: double.infinity,
              height: 52,
              child: ElevatedButton(
                onPressed: () {
                  final amt = double.tryParse(_amountController.text) ?? 0.0;
                  final purpose = _purposeController.text.trim();
                  if (amt <= 0 || purpose.isEmpty) {
                    ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(content: Text('Please enter valid amount and purpose')),
                    );
                    return;
                  }
                  _showConfirmationDialog(context, amt, purpose);
                },
                child: const Text('Review Payment Intent'),
              ),
            ),
          ],
        ),
      ),
    );
  }

  void _showConfirmationDialog(BuildContext context, double amount, String purpose) {
    showModalBottomSheet(
      context: context,
      shape: const RoundedRectangleBorder(borderRadius: BorderRadius.vertical(top: Radius.circular(24))),
      builder: (ctx) => Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text('PAYMENT SUMMARY', style: TextStyle(fontSize: 14, color: Colors.grey, fontWeight: FontWeight.bold)),
            const SizedBox(height: 16),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                const Text('Amount', style: TextStyle(fontSize: 16)),
                Text(CurrencyFormatter.formatINR(amount), style: const TextStyle(fontSize: 22, fontWeight: FontWeight.bold, color: AppColors.primary)),
              ],
            ),
            const Divider(height: 24),
            _summaryRow('Purpose', purpose),
            const SizedBox(height: 8),
            _summaryRow('Account', _selectedAccount.split(' ')[0]),
            const SizedBox(height: 8),
            _summaryRow('Method', _selectedMethod),
            const SizedBox(height: 24),
            Row(
              children: [
                Expanded(
                  child: OutlinedButton(
                    onPressed: () => Navigator.pop(ctx),
                    child: const Text('Cancel'),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: ElevatedButton(
                    onPressed: () {
                      Navigator.pop(ctx);
                      _showSuccessDialog(context, amount, purpose);
                    },
                    child: const Text('PAY NOW'),
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _summaryRow(String label, String value) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Text(label, style: const TextStyle(color: Colors.grey)),
        Text(value, style: const TextStyle(fontWeight: FontWeight.w600)),
      ],
    );
  }

  void _showSuccessDialog(BuildContext context, double amount, String purpose) {
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (ctx) => AlertDialog(
        icon: const Icon(Icons.check_circle_rounded, color: Colors.green, size: 54),
        title: const Text('Payment Successful'),
        content: Text('Payment of  for "" has been processed and recorded in your ledger.'),
        actions: [
          ElevatedButton(
            onPressed: () {
              Navigator.pop(ctx);
              Navigator.pop(context);
            },
            child: const Text('Done'),
          ),
        ],
      ),
    );
  }
}
