import 'package:intl/intl.dart';

class CurrencyFormatter {
  static String formatINR(double amount, {bool includeSymbol = true}) {
    // Format Indian Rupee currency standard, e.g. ₹1,00,000 or ₹25,000
    final format = NumberFormat.currency(
      locale: 'en_IN',
      symbol: includeSymbol ? '₹' : '',
      decimalDigits: amount.truncateToDouble() == amount ? 0 : 2,
    );
    return format.format(amount);
  }
}
