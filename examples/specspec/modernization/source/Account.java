import java.math.BigDecimal;

final class Account {
    static BigDecimal withdraw(BigDecimal balance, BigDecimal amount) {
        if (amount.compareTo(balance) > 0) {
            throw new IllegalArgumentException("DECLINED");
        }
        return balance.subtract(amount);
    }
}
