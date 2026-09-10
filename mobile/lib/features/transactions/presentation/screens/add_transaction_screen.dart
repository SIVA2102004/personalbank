import 'package:flutter/material.dart';
import '../../../core/theme/app_theme.dart';
import '../../../core/utils/currency_formatter.dart';

class AddTransactionScreen extends StatefulWidget {
  final String type; // DEBIT or CREDIT
  const AddTransactionScreen({super.key, required this.type});

  @override
  State<AddTransactionScreen> createState() => _AddTransactionScreenState();
}

class _AddTransactionScreenState extends State<AddTransactionScreen> {
  late String _type;
  final _amountController = TextEditingController();
  final _purposeController = TextEditingController();
  final _merchantController = TextEditingController();
  String _category = 'Food';
  String _account = 'SBI Savings';

  final List<String> _categories = [
    'Food', 'Transportation', 'Education', 'Shopping', 'Bills', 'Entertainment', 'Healthcare', 'Salary', 'Personal', 'Other'
  ];

  @override
  void initState() {
    super.initState();
    _type = widget.type;
  }

  @override
  Widget build(BuildContext context) {
    final isDebit = _type == 'DEBIT';

    return Scaffold(
      appBar: AppBar(title: Text(isDebit ? 'Add Expense' : 'Add Income')),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Type toggle
            Row(
              children: [
                Expanded(
                  child: ElevatedButton(
                    style: ElevatedButton.styleFrom(
                      backgroundColor: isDebit ? AppColors.expense : Colors.grey.shade300,
                      foregroundColor: isDebit ? Colors.white : Colors.black87,
                    ),
                    onPressed: () => setState(() => _type = 'DEBIT'),
                    child: const Text('Expense'),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: ElevatedButton(
                    style: ElevatedButton.styleFrom(
                      backgroundColor: !isDebit ? AppColors.accent : Colors.grey.shade300,
                      foregroundColor: !isDebit ? Colors.white : Colors.black87,
                    ),
                    onPressed: () => setState(() => _type = 'CREDIT'),
                    child: const Text('Income'),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 24),

            const Text('Amount', style: TextStyle(fontWeight: FontWeight.bold)),
            const SizedBox(height: 8),
            TextField(
              controller: _amountController,
              keyboardType: TextInputType.number,
              style: TextStyle(fontSize: 26, fontWeight: FontWeight.bold, color: isDebit ? AppColors.expense : AppColors.accent),
              decoration: const InputDecoration(
                prefixText: '₹ ',
                hintText: '0.00',
                border: OutlineInputBorder(borderRadius: BorderRadius.all(Radius.circular(12))),
              ),
            ),
            const SizedBox(height: 16),

            const Text('Purpose / Description', style: TextStyle(fontWeight: FontWeight.bold)),
            const SizedBox(height: 8),
            TextField(
              controller: _purposeController,
              decoration: const InputDecoration(
                hintText: 'e.g. Lunch at Cafe, Monthly Salary, Grocery',
                border: OutlineInputBorder(borderRadius: BorderRadius.all(Radius.circular(12))),
              ),
            ),
            const SizedBox(height: 16),

            const Text('Merchant / Person Name (Optional)', style: TextStyle(fontWeight: FontWeight.bold)),
            const SizedBox(height: 8),
            TextField(
              controller: _merchantController,
              decoration: const InputDecoration(
                hintText: 'e.g. Swiggy, Uber, Ravi',
                border: OutlineInputBorder(borderRadius: BorderRadius.all(Radius.circular(12))),
              ),
            ),
            const SizedBox(height: 16),

            const Text('Category', style: TextStyle(fontWeight: FontWeight.bold)),
            const SizedBox(height: 8),
            DropdownButtonFormField<String>(
              value: _category,
              items: _categories.map((c) => DropdownMenuItem(value: c, child: Text(c))).toList(),
              onChanged: (v) => setState(() => _category = v!),
              decoration: const InputDecoration(border: OutlineInputBorder(borderRadius: BorderRadius.all(Radius.circular(12)))),
            ),
            const SizedBox(height: 28),

            SizedBox(
              width: double.infinity,
              height: 52,
              child: ElevatedButton(
                onPressed: () {
                  final amt = double.tryParse(_amountController.text) ?? 0.0;
                  if (amt <= 0 || _purposeController.text.trim().isEmpty) {
                    ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Please enter valid amount and purpose')));
                    return;
                  }
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(content: Text(' of  recorded successfully!')),
                  );
                  Navigator.pop(context);
                },
                child: Text(isDebit ? 'Record Expense' : 'Record Income'),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
