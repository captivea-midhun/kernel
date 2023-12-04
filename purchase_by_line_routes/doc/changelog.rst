.. _changelog:

Updates
== == == =

`1.0.3`
-------
- [IMP] Account move object create method improved to get currency_id
        and company_id from context so, it will remove modules dependancy
        for POS invoice creation process or journal entry creation.

`1.0.2`
-------
- [ADD] Add track visibility(account invoice view).

`1.0.1`
-------

- [IMP] Code formatting usign pep8 and remove unnecessary space.

`1.0.0`
-------

- [ADD] Added module: account_currency_rate.
-To define your own currency rate in invoices, bills, payments and journal
entries.
-Based on your own currency rate, system will create and validate the
journal entries according to that rate.
