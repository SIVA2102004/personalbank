import 'package:flutter/material.dart';
import '../../../core/theme/app_theme.dart';
import '../../../services/api_service.dart';

class AIAssistantScreen extends StatefulWidget {
  const AIAssistantScreen({super.key});

  @override
  State<AIAssistantScreen> createState() => _AIAssistantScreenState();
}

class _AIAssistantScreenState extends State<AIAssistantScreen> {
  final _queryController = TextEditingController();
  final List<Map<String, String>> _messages = [
    {
      'role': 'assistant',
      'text': 'Hello Siva! I am your MoneyFlow AI financial assistant. Ask me questions about your spending, balances, or debts based strictly on your verified ledger.'
    }
  ];
  bool _thinking = false;

  final List<String> _suggestedQueries = [
    'How much did I spend on food?',
    'What was my largest expense?',
    'How much do I have in SBI?',
    'How much did I pay Ravi?',
  ];

  Future<void> _sendQuery(String query) async {
    if (query.trim().isEmpty) return;
    _queryController.clear();
    setState(() {
      _messages.add({'role': 'user', 'text': query});
      _thinking = true;
    });

    final answer = await apiService.queryAssistant(query);
    if (mounted) {
      setState(() {
        _messages.add({'role': 'assistant', 'text': answer});
        _thinking = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Row(
          children: [
            Icon(Icons.auto_awesome, color: Colors.blueAccent, size: 22),
            SizedBox(width: 8),
            Text('MoneyFlow AI Assistant'),
          ],
        ),
      ),
      body: Column(
        children: [
          // Suggested prompts chips
          SizedBox(
            height: 48,
            child: ListView.separated(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
              scrollDirection: Axis.horizontal,
              itemCount: _suggestedQueries.length,
              separatorBuilder: (_, __) => const SizedBox(width: 8),
              itemBuilder: (_, i) => ActionChip(
                label: Text(_suggestedQueries[i], style: const TextStyle(fontSize: 12)),
                onPressed: () => _sendQuery(_suggestedQueries[i]),
              ),
            ),
          ),
          const Divider(height: 1),

          // Messages List
          Expanded(
            child: ListView.builder(
              padding: const EdgeInsets.all(16),
              itemCount: _messages.length,
              itemBuilder: (context, i) {
                final msg = _messages[i];
                final isUser = msg['role'] == 'user';
                return Align(
                  alignment: isUser ? Alignment.centerRight : Alignment.centerLeft,
                  child: Container(
                    margin: const EdgeInsets.symmetric(vertical: 6),
                    padding: const EdgeInsets.all(14),
                    constraints: BoxConstraints(maxWidth: MediaQuery.of(context).size.width * 0.78),
                    decoration: BoxDecoration(
                      color: isUser ? AppColors.primary : Theme.of(context).cardTheme.color,
                      borderRadius: BorderRadius.circular(16),
                      border: isUser ? null : Border.all(color: Colors.grey.withOpacity(0.2)),
                    ),
                    child: Text(
                      msg['text']!,
                      style: TextStyle(
                        color: isUser ? Colors.white : null,
                        fontSize: 14,
                        height: 1.35,
                      ),
                    ),
                  ),
                );
              },
            ),
          ),

          if (_thinking)
            const Padding(
              padding: EdgeInsets.all(8.0),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  SizedBox(width: 16, height: 16, child: CircularProgressIndicator(strokeWidth: 2)),
                  SizedBox(width: 10),
                  Text('Analyzing authorized ledger records...', style: TextStyle(fontSize: 12, color: Colors.grey)),
                ],
              ),
            ),

          // Chat input field
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: Theme.of(context).cardTheme.color,
              border: Border(top: BorderSide(color: Colors.grey.withOpacity(0.2))),
            ),
            child: Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: _queryController,
                    decoration: const InputDecoration(
                      hintText: 'Ask financial assistant...',
                      border: InputBorder.none,
                      contentPadding: EdgeInsets.symmetric(horizontal: 16),
                    ),
                    onSubmitted: _sendQuery,
                  ),
                ),
                IconButton(
                  icon: const Icon(Icons.send_rounded, color: AppColors.primary),
                  onPressed: () => _sendQuery(_queryController.text),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
