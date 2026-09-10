import 'package:flutter/material.dart';
import '../../../core/theme/app_theme.dart';
import '../../../core/utils/currency_formatter.dart';
import '../../../services/api_service.dart';

class VoiceEntryScreen extends StatefulWidget {
  const VoiceEntryScreen({super.key});

  @override
  State<VoiceEntryScreen> createState() => _VoiceEntryScreenState();
}

class _VoiceEntryScreenState extends State<VoiceEntryScreen> {
  bool _isListening = false;
  String _transcript = 'I paid Ravi 500 rupees for lunch from SBI using UPI';
  Map<String, dynamic>? _extracted;

  @override
  void initState() {
    super.initState();
    _processVoiceInput(_transcript);
  }

  Future<void> _processVoiceInput(String text) async {
    final res = await apiService.parseVoice(text);
    if (mounted) {
      setState(() {
        _extracted = res;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Voice Transaction Entry')),
      body: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          children: [
            const Text(
              'Speak your transaction naturally',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 8),
            const Text(
              'e.g. "I paid Ravi 500 rupees for lunch from SBI using UPI"',
              textAlign: TextAlign.center,
              style: TextStyle(color: Colors.grey, fontSize: 13),
            ),
            const SizedBox(height: 40),

            // Microphone Visualizer
            GestureDetector(
              onTap: () {
                setState(() => _isListening = !_isListening);
                if (!_isListening) {
                  _processVoiceInput(_transcript);
                }
              },
              child: Container(
                width: 110,
                height: 110,
                decoration: BoxDecoration(
                  color: _isListening ? Colors.redAccent : AppColors.primary,
                  shape: BoxShape.circle,
                  boxShadow: [
                    BoxShadow(
                      color: (_isListening ? Colors.redAccent : AppColors.primary).withOpacity(0.35),
                      blurRadius: 20,
                      spreadRadius: 4,
                    ),
                  ],
                ),
                child: Icon(_isListening ? Icons.graphic_eq : Icons.mic, color: Colors.white, size: 54),
              ),
            ),
            const SizedBox(height: 16),
            Text(
              _isListening ? 'Listening...' : 'Tap to speak',
              style: TextStyle(fontWeight: FontWeight.w600, color: _isListening ? Colors.red : Colors.grey),
            ),

            const SizedBox(height: 32),

            // Understood Card
            if (_extracted != null) ...[
              Container(
                width: double.infinity,
                padding: const EdgeInsets.all(20),
                decoration: BoxDecoration(
                  color: Colors.green.withOpacity(0.08),
                  borderRadius: BorderRadius.circular(16),
                  border: Border.all(color: Colors.green.withOpacity(0.3)),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Row(
                      children: [
                        Icon(Icons.check_circle_outline, color: Colors.green, size: 20),
                        SizedBox(width: 8),
                        Text('I understood:', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 15)),
                      ],
                    ),
                    const SizedBox(height: 12),
                    _entityRow('Amount', CurrencyFormatter.formatINR((_extracted!['amount'] as num).toDouble())),
                    _entityRow('Person', _extracted!['person'] ?? 'None'),
                    _entityRow('Purpose', _extracted!['purpose'] ?? 'Payment'),
                    _entityRow('Category', _extracted!['category'] ?? 'Other'),
                    _entityRow('Account', _extracted!['account_hint'] ?? 'SBI'),
                    _entityRow('Method', _extracted!['payment_method'] ?? 'UPI'),
                  ],
                ),
              ),
              const Spacer(),
              Row(
                children: [
                  Expanded(
                    child: OutlinedButton(
                      onPressed: () => Navigator.pop(context),
                      child: const Text('Edit'),
                    ),
                  ),
                  const SizedBox(width: 16),
                  Expanded(
                    child: ElevatedButton(
                      onPressed: () {
                        ScaffoldMessenger.of(context).showSnackBar(
                          const SnackBar(content: Text('Voice transaction confirmed and recorded!')),
                        );
                        Navigator.pop(context);
                      },
                      child: const Text('Confirm'),
                    ),
                  ),
                ],
              ),
            ],
          ],
        ),
      ),
    );
  }

  Widget _entityRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 3),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label, style: const TextStyle(color: Colors.black54)),
          Text(value, style: const TextStyle(fontWeight: FontWeight.w600)),
        ],
      ),
    );
  }
}
