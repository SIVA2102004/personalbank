class User {
  final String id;
  final String email;
  final String fullName;
  final String preferredCurrency;
  final double monthlyIncome;

  User({
    required this.id,
    required this.email,
    required this.fullName,
    this.preferredCurrency = 'INR',
    this.monthlyIncome = 0.0,
  });

  factory User.fromJson(Map<String, dynamic> json) {
    return User(
      id: json['id'] ?? '',
      email: json['email'] ?? '',
      fullName: json['full_name'] ?? '',
      preferredCurrency: json['preferred_currency'] ?? 'INR',
      monthlyIncome: (json['monthly_income'] as num?)?.toDouble() ?? 0.0,
    );
  }
}

class Account {
  final String id;
  final String name;
  final String type;
  final String institution;
  final String? maskedIdentifier;
  final double balance;
  final String color;

  Account({
    required this.id,
    required this.name,
    required this.type,
    required this.institution,
    this.maskedIdentifier,
    required this.balance,
    this.color = '#4361EE',
  });

  factory Account.fromJson(Map<String, dynamic> json) {
    return Account(
      id: json['id'] ?? '',
      name: json['account_name'] ?? json['name'] ?? '',
      type: json['account_type'] ?? 'BANK',
      institution: json['institution_name'] ?? '',
      maskedIdentifier: json['masked_identifier'],
      balance: (json['current_balance'] ?? json['balance'] as num?)?.toDouble() ?? 0.0,
      color: json['color'] ?? '#4361EE',
    );
  }
}

class Transaction {
  final String id;
  final String accountId;
  final String? accountName;
  final String type; // CREDIT, DEBIT, TRANSFER, REFUND
  final double amount;
  final String purpose;
  final String category;
  final String? merchantName;
  final String? personName;
  final String paymentMethod;
  final String status;
  final String date;
  final bool isFlaggedUnusual;

  Transaction({
    required this.id,
    required this.accountId,
    this.accountName,
    required this.type,
    required this.amount,
    required this.purpose,
    required this.category,
    this.merchantName,
    this.personName,
    required this.paymentMethod,
    required this.status,
    required this.date,
    this.isFlaggedUnusual = false,
  });

  factory Transaction.fromJson(Map<String, dynamic> json) {
    return Transaction(
      id: json['id'] ?? '',
      accountId: json['account_id'] ?? '',
      accountName: json['account_name'],
      type: json['type'] ?? 'DEBIT',
      amount: (json['amount'] as num?)?.toDouble() ?? 0.0,
      purpose: json['purpose'] ?? '',
      category: json['category'] ?? 'Other',
      merchantName: json['merchant_name'],
      personName: json['person_name'],
      paymentMethod: json['payment_method'] ?? 'UPI',
      status: json['status'] ?? 'SUCCESS',
      date: json['date'] ?? '',
      isFlaggedUnusual: json['is_flagged_unusual'] ?? false,
    );
  }
}

class Budget {
  final String id;
  final String category;
  final double monthlyLimit;
  final double currentSpent;
  final double remaining;
  final String status;

  Budget({
    required this.id,
    required this.category,
    required this.monthlyLimit,
    required this.currentSpent,
    required this.remaining,
    required this.status,
  });

  factory Budget.fromJson(Map<String, dynamic> json) {
    return Budget(
      id: json['id'] ?? '',
      category: json['category'] ?? '',
      monthlyLimit: (json['monthly_limit'] as num?)?.toDouble() ?? 0.0,
      currentSpent: (json['current_spent'] as num?)?.toDouble() ?? 0.0,
      remaining: (json['remaining'] as num?)?.toDouble() ?? 0.0,
      status: json['status'] ?? 'NORMAL',
    );
  }
}

class SavingsGoal {
  final String id;
  final String name;
  final double targetAmount;
  final double currentSaved;
  final double progressPct;
  final double remaining;

  SavingsGoal({
    required this.id,
    required this.name,
    required this.targetAmount,
    required this.currentSaved,
    required this.progressPct,
    required this.remaining,
  });

  factory SavingsGoal.fromJson(Map<String, dynamic> json) {
    return SavingsGoal(
      id: json['id'] ?? '',
      name: json['name'] ?? '',
      targetAmount: (json['target_amount'] as num?)?.toDouble() ?? 0.0,
      currentSaved: (json['current_saved'] as num?)?.toDouble() ?? 0.0,
      progressPct: (json['progress_pct'] as num?)?.toDouble() ?? 0.0,
      remaining: (json['remaining'] as num?)?.toDouble() ?? 0.0,
    );
  }
}

class Person {
  final String id;
  final String name;
  final String? phone;
  final String? upiId;
  final double netBalance; // >0 they owe you, <0 you owe them

  Person({
    required this.id,
    required this.name,
    this.phone,
    this.upiId,
    required this.netBalance,
  });

  factory Person.fromJson(Map<String, dynamic> json) {
    return Person(
      id: json['id'] ?? '',
      name: json['name'] ?? '',
      phone: json['phone'],
      upiId: json['upi_id'],
      netBalance: (json['net_balance'] as num?)?.toDouble() ?? 0.0,
    );
  }
}
