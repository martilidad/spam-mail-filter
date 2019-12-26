# spam-mail-filter
A spam filter for E-mails via IMAP-Protocol.
Various features are used to classify spam:
* Mail-Body via Bayesian Network
* Mail-Subject via Bayesian Network
* URLs in the mail via Google Safe Browsing API
* Mail-Sender via a Blacklist

## Running the Application
After you have specified all required required configuration values in the spamfilter.ini file (see next section), you
can simply start the application via docker or with your local python installation (see requirements.txt for dependencies).

If the application is started in the 'USERMAIL_TRAINING' or 'ONLINE_TRAINING' start-mode, it can be trained further with
new mails if you enter 'train' in the console. This training is synchronized with the mail-check.

### Configuration
The application can be configured by providing the values in the spamfilter.ini file or by using command line arguments.
If both are specified, the command line arguments overwrite the values in the config-file.
To see the possible configuration values, run the application with the -h argument.

Some configurations are required. A default value is used for optional values if they are omitted.
The config-file is separated in different section:

##### Mail-Settings
| Config-Key | required | default value | description                                                     |
| -----------|:--------:|:-------------:|-----------------------------------------------------------------|
| username   | yes      | -             | The username / email-address of the email-account to be checked |
| password   | yes      | -             | The password for the email-account to be checked                |
| host       | yes      | -             | The imap-host-address of the mail-server                        |
| port       | no       | 993           | The imap-port of the mail-server                                |
| ssl        | no       | True          | A flag that indicates whether or not you want to connect to the mail-server using SSL |

##### Mailbox-Settings
| Config-Key         | required | default value | description                                          |
| -------------------|:--------:|:-------------:|------------------------------------------------------|
| inbox              | yes      | -             | The mailbox to check for spam                        |
| spam_mailbox       | yes      | -             | The mailbox into which spam mails are to be moved    |
| train_ham_mailbox  | yes      | -             | The mailbox that you want to use to train ham mails  |
| train_spam_mailbox | yes      | -             | The mailbox that you want to use to train spam mails |

##### Spam-Classification Settings
| Config-Key      | required | default value | description                                           |
| ----------------|:--------:|:-------------:|-------------------------------------------------------|
| score_threshold | no       | 0.5           | The thresholds from which an email is treated as spam |
| check_interval  | no       | 15            | The interval at which spam is regularly filtered      |

##### Classification-Weight Settings
It is possible to configure the weight of each feature with which it contributes to the total score. The sum of all
weights must be at least 1, but can also be higher.

| Config-Key     | required | default value | description                                                           |
| ---------------|:--------:|:-------------:|-----------------------------------------------------------------------|
| body_weight    | no       | 0             | The weight with which the mail body contributes to the total score    |
| subject_weight | no       | 0             | The weight with which the mail subject contributes in the total score |
| url_weight     | no       | 0             | The weight with which urls in the mail contributes in the total score |
| from_weight    | no       | 0             | The weight with which the sender contributes in the total score       |

##### Process Settings
| Config-Key        | required | default value     | description                                                                               |
| ------------------|:--------:|:-----------------:|-------------------------------------------------------------------------------------------|
| start_mode        | no       | USERMAIL_TRAINING | The mode in which the application is started and trained. See section 'Modes' for details |
| check_mode        | no       | NORMAL            | The mode im which spam mails are handled. See section 'Modes' for details                 |
| max_train_mails   | no       | 500               | The maximum amount of mails used for training from each mailbox                           |
| batch_size        | no       | 100               | The amount of mails that are retrieved at once from the mail server                       |
| console_log_level | no       | INFO              | The level at which the application should be logged                                       |
| create_logfiles   | no       | False             | A flag that indicates whether a logfile should be created                                 |

##### External Settings
| Config-Key       | required                             | default value | description                                                                               |
| -----------------|:------------------------------------:|:-------------:|-------------------------------------------------------------------------------------------|
| google_api_token | only if url_weight is greater than 0 | -             | The API-key to access the Google Safe Browsing API. See the API documentation for details |

#### Modes
It is possible to specify the Start-Mode (config-key start_mode) and the Check-Mode (config-key check_mode)
The possible values and there effects are described here:

##### Start-Mode
| Mode              | description                                                                                         |
| ------------------|-----------------------------------------------------------------------------------------------------|
| PRETRAINED        | The Bayesian Network is deserialized from a previously trained run                                  |
| USERMAIL_TRAINING | The mails from the specified mailboxes are used for the training                                    |
| ONLINE_TRAINING   | The Bayesian Network is first deserialized from a previously trained run and then further learned  from the mails in the specified mailboxes |
| TESTDATA_TRAINING | The provided test mails will be used for training                                                   |
| NO_TRAINING       | No training will be performed. This only makes sense if the weight for body and subject is set to 0 |
| LIST_MAIL_FOLDERS | Available mailboxes for the mailbox settings will be listed. The application then shuts down        |

##### Check-Mode
| Mode     | description                                               |
| ---------|-----------------------------------------------------------|
| NONE     | Only the training will be performed. No mails are checked |
| NORMAL   | Detected spam mails are moved to the specified mailbox    |
| FLAGGING | Instead of moving mails, they are only flagged            |
| DRYRUN   | Mails are checked, but neither flagged nor moved          |
