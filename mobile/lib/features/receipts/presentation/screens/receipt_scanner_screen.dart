import 'package:flutter/material.dart';
import '../../../core/theme/app_theme.dart';
import '../../../core/utils/currency_formatter.dart';
import '../../../services/api_service.dart';

class ReceiptScannerScreen extends StatefulWidget {
  const ReceiptScannerScreen({super.key});

  @override
  State<ReceiptScannerScreen> createState() => _ReceiptScannerScreenState();
}

class _ReceiptScannerScreenState extends State<ReceiptScannerScreen> {
  bool _scanning = false;
  Map<String, dynamic>? _receiptData;

  Future<void> _scanReceipt() async {
    setState(() => _scanning = true);
    final res = await apiService.scanReceipt();
    if (mounted) {
      setState(() {
        _receiptData = res;
        _scanning = false;
      });
    }
  }

  @override
  void initState() {
    super.initState();
    _scanReceipt();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Receipt Scanner (OCR)')),
      body: _scanning
          ? const Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  CircularProgressIndicator(),
                  SizedBox(height: 16),
                  Text('Extracting items and merchant via Vision AI...', style: TextStyle(color: Colors.grey)),
                ],
              ),
            )
          : SingleChildScrollView(
              padding: const EdgeInsets.all(20),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Receipt Card
                  Container(
                    width: double.infinity,
                    padding: const EdgeInsets.all(20),
                    decoration: BoxDecoration(
                      color: Theme.of(context).cardTheme.color,
                      borderRadius: BorderRadius.circular(16),
                      border: Border.all(color: Colors.grey.withOpacity(0.3)),
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            Text(
                              _receiptData?['merchant'] ?? 'Merchant',
                              style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                            ),
                            Chip(
                              label: Text(_receiptData?['category'] ?? 'Groceries'),
                              backgroundColor: AppColors.primaryLight.withOpacity(0.1),
                            ),
                          ],
                        ),
                        Text(
                          'Date: ',
                          style: const TextStyle(color: Colors.grey, fontSize: 13),
                        ),
                        const Divider(height: 24),
                        const Text('Items Extracted:', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 14)),
                        const SizedBox(height: 8),
                        ...?(_receiptData?['items'] as List?)?.map((item) => Padding(
                              padding: const EdgeInsets.symmetric(vertical: 4),
                              child: Row(
                                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                children: [
                                  Text('x '),
                                  Text(CurrencyFormatter.formatINR((item['price'] as num).toDouble())),
                                ],
                              ),
                            )),
                        const Divider(height: 24),
                        Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            const Text('Total Amount', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
                            Text(
                              CurrencyFormatter.formatINR((_receiptData?['total'] as num?)?.toDouble() ?? 1245.50),
                              style: const TextStyle(fontSize: 22, fontWeight: FontWeight.bold, color: AppColors.primary),
                            ),
                          ],
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: 24),
                  SizedBox(
                    width: double.infinity,
                    height: 52,
                    child: ElevatedButton(
                      onPressed: () {
                        ScaffoldMessenger.of(context).showSnackBar(
                          const SnackBar(content: Text('Receipt transaction saved to ledger!')),
                        );
                        Navigator.pop(context);
                      },
                      child: const Text('Confirm & Save Transaction'),
                    ),
                  ),
                ],
              ),
            ),
    );
  }
}
