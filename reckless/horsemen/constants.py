

# Constants
METERS_PER_FURLONG = 201.168
METERS_PER_LENGTH = 2.4384

# Models Choices
EQUIBASE_SEX_RESTRICTIONS_CHOICES = [
    ('N', 'No sex restrictions'),
    ('M', 'Mares and fillies only'),
    ('C', 'Colts and/or geldings only'),
    ('F', 'Fillies only'),
]

RACE_SURFACE = [
    ('D', 'Dirt'),
    ('T', 'Turf')
]

EQUIBASE_RACE_TYPE_CHOICES = [
    ('ALW', 'Allowance race'),
    ('AOC', 'Allowance/Optional Claiming'),
    ('CLH', 'Claiming Handicap'),
    ('CLM', 'Claiming'),
    ('CST', 'Claiming Stakes'),
    ('HCP', 'Handicap'),
    ('MAT', 'Match Race'),
    ('MCL', 'Maiden Claiming'),
    ('MOC', 'Maiden Optional Claiming'),
    ('MSA', 'Maiden Starter Allowance'),
    ('MSW', 'Maiden Special Weight'),
    ('MST', 'Maiden Stakes'),
    ('OCH', 'Optional Claiming Handicap'),
    ('OCL', 'Optional Claiming'),
    ('SHP', 'Starter Handicap'),
    ('SOC', 'Starter/Optional Claiming'),
    ('SST', 'Starter Stakes'),
    ('STK', 'Stakes'),
    ('STR', 'Starter Allowance'),
    ('TRL', 'Trial'),
    ('WCL', 'Waiver Claiming'),
    ('WMC', 'Waiver Maiden Claiming'),
    
    # Quarter Horse and Mixed Breed Race Types
    ('ALWFL', 'Allowance Final'),
    ('AWT', 'Allowance Trial'),
    ('CAN', 'Cancelled'),
    ('CHM', 'Championship'),
    ('CLS', 'Claiming Stakes'),
    ('CLT', 'Claiming Stakes Trial'),
    ('CON', 'Consolation'),
    ('CST', 'Claiming Stakes/Trial'),
    ('DBY', 'Derby'),
    ('DBYFL', 'Derby Final'),
    ('DCN', 'Derby Consolation'),
    ('DTR', 'Derby Trial'),
    ('EXH', 'Exhibition'),
    ('FCN', 'Futurity Consolation'),
    ('FNL', 'Final'),
    ('FTR', 'Futurity Trial'),
    ('FUT', 'Futurity'),
    ('FUTFL', 'Futurity Final'),
    ('HDS', 'Handicap Stakes'),
    ('IHS', 'Invitational Handicap Stakes'),
    ('INH', 'Invitational Handicap'),
    ('INS', 'Invitational Stakes'),
    ('INV', 'Invitational'),
    ('MCL', 'Maiden Claiming'),
    ('MCN', 'Maturity Consolation'),
    ('MATFL', 'Maturity Final'),
    ('MCH', 'Match Race'),
    ('MDN', 'Maiden'),
    ('MDT', 'Maiden Trial'),
    ('MOC', 'Maiden Optional Claiming'),
    ('MSA', 'Maiden Starter Allowance'),
    ('MTR', 'Maturity Trial'),
    ('OCL', 'Optional Claiming'),
    ('SCN', 'Stakes Consolation'),
    ('SHP', 'Starter Handicap'),
    ('SOC', 'Starter Optional Claiming'),
    ('SPC', 'Speed Index Consolation'),
    ('SPF', 'Speed Index Final'),
    ('SPI', 'Speed Index Race'),
    ('SPT', 'Speed Index Trial'),
    ('STA', 'Starter Allowance'),
    ('STK', 'Stakes'),
    ('STR', 'Stakes Trial'),
    ('TRL', 'Trials'),
    ('UNK', 'Unknown Race Type'),
    ('WCL', 'Waiver Claiming'),
    ('ZRC', 'Cancelled Race'),
]

DAY_EVENING_CHOICES = [
    ('D', 'Day'),
    ('E', 'Evening')
]

DRF_AGE_RESTRICTION_CHOICES = [
    ('02', 'Two year old'),
    ('03', 'Three year old'),
    ('04', 'Four year old'),
    ('05', 'Five year old'),
    ('06', 'Six year old'),
    ('07', 'Seven year old'),
    ('08', 'Eight year old'),
    ('09', 'Nine year old'),
    ('23', 'Two and Three year olds'),
    ('2U', 'Two year olds and older'),
    ('34', 'Three and Four year olds'),
    ('35', 'Three, Four, and Five year olds'),
    ('36', 'Three, Four, Five, and Six year olds'),
    ('3U', 'Three year olds and older'),
    ('45', 'Four and Five year olds'),
    ('46', 'Four, Five, and Six year olds'),
    ('47', 'Four, Five, Six, and Seven year olds'),
    ('4U', 'Four year olds and older'),
    ('56', 'Five and Six year olds'),
    ('57', 'Five, Six, and Seven year olds'),
    ('58', 'Five, Six, Seven, and Eight year olds'),
    ('59', 'Five, Six, Seven, Eight, and Nine year olds'),
    ('5U', 'Five year olds and older'),
    ('67', 'Six and Seven year olds'),
    ('68', 'Six, Seven, and Eight year olds'),
    ('69', 'Six, Seven, Eight, and Nine year olds'),
    ('6U', 'Six year olds and older'),
    ('78', 'Seven and Eight year olds'),
    ('79', 'Seven, Eight, and Nine year olds'),
    ('7U', 'Seven year olds and older'),
    ('8U', 'Eight year olds and older'),
    ('9U', 'Nine year olds and older'),
]

DRF_SEX_RESTRICTION_CHOICES = [
    ('O', 'Open'),             # Blank or open
    ('A', 'C & G (colts and geldings)'),  # Colts and geldings
    ('B', 'F & M (fillies and mares)'),  # Fillies and mares
    ('C', 'C (colts)'),       # Colts
    ('D', 'C & F (colts and fillies)'),  # Colts and fillies
    ('E', 'F & G (fillies and geldings)'),  # Fillies and geldings
    ('F', 'F (fillies)'),     # Fillies
    ('G', 'G (geldings)'),   # Geldings
    ('H', 'H (horses only)'),  # Horses only
    ('M', 'M (mares only)'),  # Mares only
]

BREED_CHOICES = [
    ('TB', 'Thoroughbred'),   # Thoroughbred
    ('QH', 'Quarter Horse'),  # Quarter Horse
    ('AR', 'Arabian'),        # Arabian
    ('PT', 'Paint'),          # Paint
    ('MX', 'Mixed Breeds'),   # Mixed Breeds
]

# Resources
POINTS_OF_CALL_QH = [
  {
    "distance": "Less than 330 yards",
    "floor": 0,
    "calls": [
      {
        "point": 1,
        "text": "Start"
      },
      {
        "point": 5,
        "text": "Str"
      },
      {
        "point": 6,
        "text": "Fin"
      }
    ]
  },
  {
    "distance": "330 Yards and Longer",
    "floor": 990,
    "calls": [
      {
        "point": 1,
        "text": "Start"
      },
      {
        "point": 2,
        "text": "Str1"
      },
      {
        "point": 5,
        "text": "Str"
      },
      {
        "point": 6,
        "text": "Fin"
      }
    ]
  }
]


POINTS_OF_CALL = [
  {
    "distance": "150 yards",
    "floor": 450,
    "calls": [
      {
        "point": 1,
        "text": "Start"
      },
      {
        "point": 5,
        "text": "Str"
      },
      {
        "point": 6,
        "text": "Fin",
        "feet": 450
      }
    ]
  },
  {
    "distance": "1 furlong",
    "floor": 660,
    "calls": [
      {
        "point": 1,
        "text": "Start"
      },
      {
        "point": 5,
        "text": "Str"
      },
      {
        "point": 6,
        "text": "Fin",
        "feet": 660
      }
    ]
  },
  {
    "distance": "2 furlongs",
    "floor": 1320,
    "calls": [
      {
        "point": 1,
        "text": "Start"
      },
      {
        "point": 5,
        "text": "Str",
        "feet": 660
      },
      {
        "point": 6,
        "text": "Fin",
        "feet": 1320
      }
    ]
  },
  {
    "distance": "3 furlongs",
    "floor": 1980,
    "calls": [
      {
        "point": 1,
        "text": "Start"
      },
      {
        "point": 5,
        "text": "Str",
        "feet": 1320
      },
      {
        "point": 6,
        "text": "Fin",
        "feet": 1980
      }
    ]
  },
  {
    "distance": "3 1/4 furlongs",
    "floor": 2145,
    "calls": [
      {
        "point": 1,
        "text": "Start"
      },
      {
        "point": 2,
        "text": "1/4",
        "feet": 1320
      },
      {
        "point": 5,
        "text": "Str",
        "feet": 1485
      },
      {
        "point": 6,
        "text": "Fin",
        "feet": 2145
      }
    ]
  },
  {
    "distance": "4 furlongs",
    "floor": 2640,
    "calls": [
      {
        "point": 1,
        "text": "Start"
      },
      {
        "point": 2,
        "text": "1/4",
        "feet": 1320
      },
      {
        "point": 5,
        "text": "Str",
        "feet": 1980
      },
      {
        "point": 6,
        "text": "Fin",
        "feet": 2640
      }
    ]
  },
  {
    "distance": "4 1/2 furlongs",
    "floor": 2970,
    "calls": [
      {
        "point": 1,
        "text": "Start"
      },
      {
        "point": 2,
        "text": "1/4",
        "feet": 1320
      },
      {
        "point": 5,
        "text": "Str",
        "feet": 2310
      },
      {
        "point": 6,
        "text": "Fin",
        "feet": 2970
      }
    ]
  },
  {
    "distance": "1000 yards",
    "floor": 3000,
    "calls": [
      {
        "point": 5,
        "text": "Str",
        "feet": 2310
      },
      {
        "point": 6,
        "text": "Fin",
        "feet": 2970
      }
    ]
  },
  {
    "distance": "5 furlongs",
    "floor": 3300,
    "calls": [
      {
        "point": 1,
        "text": "Start"
      },
      {
        "point": 2,
        "text": "3/16",
        "feet": 990
      },
      {
        "point": 3,
        "text": "3/8",
        "feet": 1980
      },
      {
        "point": 5,
        "text": "Str",
        "feet": 2640
      },
      {
        "point": 6,
        "text": "Fin",
        "feet": 3300
      }
    ]
  },
  {
    "distance": "5 1/2 furlongs",
    "floor": 3630,
    "calls": [
      {
        "point": 1,
        "text": "Start"
      },
      {
        "point": 2,
        "text": "1/4",
        "feet": 1320
      },
      {
        "point": 3,
        "text": "3/8",
        "feet": 1980
      },
      {
        "point": 5,
        "text": "Str",
        "feet": 2970
      },
      {
        "point": 6,
        "text": "Fin",
        "feet": 3630
      }
    ]
  },
  {
    "distance": "6 furlongs",
    "floor": 3960,
    "calls": [
      {
        "point": 1,
        "text": "Start"
      },
      {
        "point": 2,
        "text": "1/4",
        "feet": 1320
      },
      {
        "point": 3,
        "text": "1/2",
        "feet": 2640
      },
      {
        "point": 5,
        "text": "Str",
        "feet": 3300
      },
      {
        "point": 6,
        "text": "Fin",
        "feet": 3960
      }
    ]
  },
  {
    "distance": "6 1/2 furlongs",
    "floor": 4290,
    "calls": [
      {
        "point": 1,
        "text": "Start"
      },
      {
        "point": 2,
        "text": "1/4",
        "feet": 1320
      },
      {
        "point": 3,
        "text": "1/2",
        "feet": 2640
      },
      {
        "point": 5,
        "text": "Str",
        "feet": 3630
      },
      {
        "point": 6,
        "text": "Fin",
        "feet": 4290
      }
    ]
  },
  {
    "distance": "7 furlongs",
    "floor": 4620,
    "calls": [
      {
        "point": 1,
        "text": "Start"
      },
      {
        "point": 2,
        "text": "1/4",
        "feet": 1320
      },
      {
        "point": 3,
        "text": "1/2",
        "feet": 2640
      },
      {
        "point": 5,
        "text": "Str",
        "feet": 3960
      },
      {
        "point": 6,
        "text": "Fin",
        "feet": 4620
      }
    ]
  },
  {
    "distance": "7 1/2 furlongs",
    "floor": 4950,
    "calls": [
      {
        "point": 1,
        "text": "Start"
      },
      {
        "point": 2,
        "text": "1/4",
        "feet": 1320
      },
      {
        "point": 3,
        "text": "1/2",
        "feet": 2640
      },
      {
        "point": 5,
        "text": "Str",
        "feet": 4290
      },
      {
        "point": 6,
        "text": "Fin",
        "feet": 4950
      }
    ]
  },
  {
    "distance": "1 mile",
    "floor": 5280,
    "calls": [
      {
        "point": 1,
        "text": "Start"
      },
      {
        "point": 2,
        "text": "1/4",
        "feet": 1320
      },
      {
        "point": 3,
        "text": "1/2",
        "feet": 2640
      },
      {
        "point": 4,
        "text": "3/4",
        "feet": 3960
      },
      {
        "point": 5,
        "text": "Str",
        "feet": 4620
      },
      {
        "point": 6,
        "text": "Fin",
        "feet": 5280
      }
    ]
  },
  {
    "distance": "1 mile 30 yards",
    "floor": 5370,
    "calls": [
      {
        "point": 1,
        "text": "Start"
      },
      {
        "point": 2,
        "text": "1/4",
        "feet": 1320
      },
      {
        "point": 3,
        "text": "1/2",
        "feet": 2640
      },
      {
        "point": 4,
        "text": "3/4",
        "feet": 3960
      },
      {
        "point": 5,
        "text": "Str",
        "feet": 4710
      },
      {
        "point": 6,
        "text": "Fin",
        "feet": 5370
      }
    ]
  },
  {
    "distance": "1 mile 40 yards",
    "floor": 5400,
    "calls": [
      {
        "point": 1,
        "text": "Start"
      },
      {
        "point": 2,
        "text": "1/4",
        "feet": 1320
      },
      {
        "point": 3,
        "text": "1/2",
        "feet": 2640
      },
      {
        "point": 4,
        "text": "3/4",
        "feet": 3960
      },
      {
        "point": 5,
        "text": "Str",
        "feet": 4740
      },
      {
        "point": 6,
        "text": "Fin",
        "feet": 5400
      }
    ]
  },
  {
    "distance": "1 mile 70 yards",
    "floor": 5490,
    "calls": [
      {
        "point": 1,
        "text": "Start"
      },
      {
        "point": 2,
        "text": "1/4",
        "feet": 1320
      },
      {
        "point": 3,
        "text": "1/2",
        "feet": 2640
      },
      {
        "point": 4,
        "text": "3/4",
        "feet": 3960
      },
      {
        "point": 5,
        "text": "Str",
        "feet": 4830
      },
      {
        "point": 6,
        "text": "Fin",
        "feet": 5490
      }
    ]
  },
  {
    "distance": "1 1/16 miles",
    "floor": 5610,
    "calls": [
      {
        "point": 1,
        "text": "Start"
      },
      {
        "point": 2,
        "text": "1/4",
        "feet": 1320
      },
      {
        "point": 3,
        "text": "1/2",
        "feet": 2640
      },
      {
        "point": 4,
        "text": "3/4",
        "feet": 3960
      },
      {
        "point": 5,
        "text": "Str",
        "feet": 4950
      },
      {
        "point": 6,
        "text": "Fin",
        "feet": 5610
      }
    ]
  },
  {
    "distance": "1 1/8 miles",
    "floor": 5940,
    "calls": [
      {
        "point": 1,
        "text": "Start"
      },
      {
        "point": 2,
        "text": "1/4",
        "feet": 1320
      },
      {
        "point": 3,
        "text": "1/2",
        "feet": 2640
      },
      {
        "point": 4,
        "text": "3/4",
        "feet": 3960
      },
      {
        "point": 5,
        "text": "Str",
        "feet": 5280
      },
      {
        "point": 6,
        "text": "Fin",
        "feet": 5940
      }
    ]
  },
  {
    "distance": "1 3/16 miles",
    "floor": 6270,
    "calls": [
      {
        "point": 1,
        "text": "Start"
      },
      {
        "point": 2,
        "text": "1/4",
        "feet": 1320
      },
      {
        "point": 3,
        "text": "1/2",
        "feet": 2640
      },
      {
        "point": 4,
        "text": "3/4",
        "feet": 3960
      },
      {
        "point": 5,
        "text": "Str",
        "feet": 5610
      },
      {
        "point": 6,
        "text": "Fin",
        "feet": 6270
      }
    ]
  },
  {
    "distance": "1 1/4 miles",
    "floor": 6600,
    "calls": [
      {
        "point": 1,
        "text": "1/4",
        "feet": 1320
      },
      {
        "point": 2,
        "text": "1/2",
        "feet": 2640
      },
      {
        "point": 3,
        "text": "3/4",
        "feet": 3960
      },
      {
        "point": 4,
        "text": "1m",
        "feet": 5280
      },
      {
        "point": 5,
        "text": "Str",
        "feet": 5940
      },
      {
        "point": 6,
        "text": "Fin",
        "feet": 6600
      }
    ]
  },
  {
    "distance": "1 5/16 miles",
    "floor": 6930,
    "calls": [
      {
        "point": 1,
        "text": "1/4",
        "feet": 1320
      },
      {
        "point": 2,
        "text": "1/2",
        "feet": 2640
      },
      {
        "point": 3,
        "text": "3/4",
        "feet": 3960
      },
      {
        "point": 4,
        "text": "1m",
        "feet": 5280
      },
      {
        "point": 5,
        "text": "Str",
        "feet": 6270
      },
      {
        "point": 6,
        "text": "Fin",
        "feet": 6930
      }
    ]
  },
  {
    "distance": "1 3/8 miles",
    "floor": 7260,
    "calls": [
      {
        "point": 1,
        "text": "1/4",
        "feet": 1320
      },
      {
        "point": 2,
        "text": "1/2",
        "feet": 2640
      },
      {
        "point": 3,
        "text": "3/4",
        "feet": 3960
      },
      {
        "point": 4,
        "text": "1m",
        "feet": 5280
      },
      {
        "point": 5,
        "text": "Str",
        "feet": 6600
      },
      {
        "point": 6,
        "text": "Fin",
        "feet": 7260
      }
    ]
  },
  {
    "distance": "1 7/16 miles",
    "floor": 7590,
    "calls": [
      {
        "point": 1,
        "text": "1/4",
        "feet": 1320
      },
      {
        "point": 2,
        "text": "1/2",
        "feet": 2640
      },
      {
        "point": 3,
        "text": "1m",
        "feet": 5280
      },
      {
        "point": 4,
        "text": "11/4",
        "feet": 6600
      },
      {
        "point": 5,
        "text": "Str",
        "feet": 6930
      },
      {
        "point": 6,
        "text": "Fin",
        "feet": 7590
      }
    ]
  },
  {
    "distance": "1 1/2 miles",
    "floor": 7920,
    "calls": [
      {
        "point": 1,
        "text": "1/4",
        "feet": 1320
      },
      {
        "point": 2,
        "text": "1/2",
        "feet": 2640
      },
      {
        "point": 3,
        "text": "1m",
        "feet": 5280
      },
      {
        "point": 4,
        "text": "11/4",
        "feet": 6600
      },
      {
        "point": 5,
        "text": "Str",
        "feet": 7260
      },
      {
        "point": 6,
        "text": "Fin",
        "feet": 7920
      }
    ]
  },
  {
    "distance": "1 9/16 miles",
    "floor": 8250,
    "calls": [
      {
        "point": 1,
        "text": "1/4",
        "feet": 1320
      },
      {
        "point": 2,
        "text": "1/2",
        "feet": 2640
      },
      {
        "point": 3,
        "text": "1m",
        "feet": 5280
      },
      {
        "point": 4,
        "text": "11/4",
        "feet": 6600
      },
      {
        "point": 5,
        "text": "Str",
        "feet": 7590
      },
      {
        "point": 6,
        "text": "Fin",
        "feet": 8250
      }
    ]
  },
  {
    "distance": "1 5/8 miles",
    "floor": 8580,
    "calls": [
      {
        "point": 1,
        "text": "1/4",
        "feet": 1320
      },
      {
        "point": 2,
        "text": "1/2",
        "feet": 2640
      },
      {
        "point": 3,
        "text": "1m",
        "feet": 5280
      },
      {
        "point": 4,
        "text": "13/8",
        "feet": 7260
      },
      {
        "point": 5,
        "text": "Str",
        "feet": 7920
      },
      {
        "point": 6,
        "text": "Fin",
        "feet": 8580
      }
    ]
  },
  {
    "distance": "1 11/16 miles",
    "floor": 8910,
    "calls": [
      {
        "point": 1,
        "text": "1/4",
        "feet": 1320
      },
      {
        "point": 2,
        "text": "1/2",
        "feet": 2640
      },
      {
        "point": 3,
        "text": "1m",
        "feet": 5280
      },
      {
        "point": 4,
        "text": "13/8",
        "feet": 7260
      },
      {
        "point": 5,
        "text": "Str",
        "feet": 8250
      },
      {
        "point": 6,
        "text": "Fin",
        "feet": 8910
      }
    ]
  },
  {
    "distance": "1 3/4 miles",
    "floor": 9240,
    "calls": [
      {
        "point": 1,
        "text": "1/2",
        "feet": 2640
      },
      {
        "point": 2,
        "text": "1m",
        "feet": 5280
      },
      {
        "point": 3,
        "text": "11/4",
        "feet": 6600
      },
      {
        "point": 4,
        "text": "11/2",
        "feet": 7920
      },
      {
        "point": 5,
        "text": "Str",
        "feet": 8580
      },
      {
        "point": 6,
        "text": "Fin",
        "feet": 9240
      }
    ]
  },
  {
    "distance": "1 13/16 miles",
    "floor": 9570,
    "calls": [
      {
        "point": 1,
        "text": "1/2",
        "feet": 2640
      },
      {
        "point": 2,
        "text": "1m",
        "feet": 5280
      },
      {
        "point": 3,
        "text": "11/4",
        "feet": 6600
      },
      {
        "point": 4,
        "text": "11/2",
        "feet": 7920
      },
      {
        "point": 5,
        "text": "Str",
        "feet": 8910
      },
      {
        "point": 6,
        "text": "Fin",
        "feet": 9570
      }
    ]
  },
  {
    "distance": "1 7/8 miles",
    "floor": 9900,
    "calls": [
      {
        "point": 1,
        "text": "1/2",
        "feet": 2640
      },
      {
        "point": 2,
        "text": "1m",
        "feet": 5280
      },
      {
        "point": 3,
        "text": "11/4",
        "feet": 6600
      },
      {
        "point": 4,
        "text": "11/2",
        "feet": 7920
      },
      {
        "point": 5,
        "text": "Str",
        "feet": 9240
      },
      {
        "point": 6,
        "text": "Fin",
        "feet": 9900
      }
    ]
  },
  {
    "distance": "1 15/16 miles",
    "floor": 10230,
    "calls": [
      {
        "point": 1,
        "text": "1/2",
        "feet": 2640
      },
      {
        "point": 2,
        "text": "1m",
        "feet": 5280
      },
      {
        "point": 3,
        "text": "13/8",
        "feet": 7260
      },
      {
        "point": 4,
        "text": "15/8",
        "feet": 8580
      },
      {
        "point": 5,
        "text": "Str",
        "feet": 9570
      },
      {
        "point": 6,
        "text": "Fin",
        "feet": 10230
      }
    ]
  },
  {
    "distance": "2 miles",
    "floor": 10560,
    "calls": [
      {
        "point": 1,
        "text": "1/2",
        "feet": 2640
      },
      {
        "point": 2,
        "text": "1m",
        "feet": 5280
      },
      {
        "point": 3,
        "text": "11/2",
        "feet": 7920
      },
      {
        "point": 4,
        "text": "13/4",
        "feet": 9240
      },
      {
        "point": 5,
        "text": "Str",
        "feet": 9900
      },
      {
        "point": 6,
        "text": "Fin",
        "feet": 10560
      }
    ]
  },
  {
    "distance": "2 miles 40 yards",
    "floor": 10680,
    "calls": [
      {
        "point": 1,
        "text": "1/2",
        "feet": 2640
      },
      {
        "point": 2,
        "text": "1m",
        "feet": 5280
      },
      {
        "point": 3,
        "text": "11/2",
        "feet": 7920
      },
      {
        "point": 4,
        "text": "13/4",
        "feet": 9240
      },
      {
        "point": 5,
        "text": "Str",
        "feet": 10020
      },
      {
        "point": 6,
        "text": "Fin",
        "feet": 10680
      }
    ]
  },
  {
    "distance": "2 miles 70 yards",
    "floor": 10770,
    "calls": [
      {
        "point": 1,
        "text": "1/2",
        "feet": 2640
      },
      {
        "point": 2,
        "text": "1m",
        "feet": 5280
      },
      {
        "point": 3,
        "text": "11/2",
        "feet": 7920
      },
      {
        "point": 4,
        "text": "13/4",
        "feet": 9240
      },
      {
        "point": 5,
        "text": "Str",
        "feet": 10110
      },
      {
        "point": 6,
        "text": "Fin",
        "feet": 10770
      }
    ]
  },
  {
    "distance": "2 1/16 miles",
    "floor": 10890,
    "calls": [
      {
        "point": 1,
        "text": "1/2",
        "feet": 2640
      },
      {
        "point": 2,
        "text": "1m",
        "feet": 5280
      },
      {
        "point": 3,
        "text": "11/2",
        "feet": 7920
      },
      {
        "point": 4,
        "text": "13/4",
        "feet": 9240
      },
      {
        "point": 5,
        "text": "Str",
        "feet": 10230
      },
      {
        "point": 6,
        "text": "Fin",
        "feet": 10890
      }
    ]
  },
  {
    "distance": "2 1/8 miles",
    "floor": 11220,
    "calls": [
      {
        "point": 1,
        "text": "1/2",
        "feet": 2640
      },
      {
        "point": 2,
        "text": "1m",
        "feet": 5280
      },
      {
        "point": 3,
        "text": "11/2",
        "feet": 7920
      },
      {
        "point": 4,
        "text": "13/4",
        "feet": 9240
      },
      {
        "point": 5,
        "text": "Str",
        "feet": 10560
      },
      {
        "point": 6,
        "text": "Fin",
        "feet": 11220
      }
    ]
  },
  {
    "distance": "2 3/16 miles",
    "floor": 11550,
    "calls": [
      {
        "point": 1,
        "text": "1/2",
        "feet": 2640
      },
      {
        "point": 2,
        "text": "1m",
        "feet": 5280
      },
      {
        "point": 3,
        "text": "11/2",
        "feet": 7920
      },
      {
        "point": 4,
        "text": "13/4",
        "feet": 9240
      },
      {
        "point": 5,
        "text": "Str",
        "feet": 10890
      },
      {
        "point": 6,
        "text": "Fin",
        "feet": 11550
      }
    ]
  },
  {
    "distance": "2 1/4 miles",
    "floor": 11880,
    "calls": [
      {
        "point": 1,
        "text": "1/2",
        "feet": 2640
      },
      {
        "point": 2,
        "text": "1m",
        "feet": 5280
      },
      {
        "point": 3,
        "text": "11/2",
        "feet": 7920
      },
      {
        "point": 4,
        "text": "2m",
        "feet": 10560
      },
      {
        "point": 5,
        "text": "Str",
        "feet": 11220
      },
      {
        "point": 6,
        "text": "Fin",
        "feet": 11880
      }
    ]
  },
  {
    "distance": "2 5/16 miles",
    "floor": 12210,
    "calls": [
      {
        "point": 1,
        "text": "1/2",
        "feet": 2640
      },
      {
        "point": 2,
        "text": "1m",
        "feet": 5280
      },
      {
        "point": 3,
        "text": "11/2",
        "feet": 7920
      },
      {
        "point": 4,
        "text": "2m",
        "feet": 10560
      },
      {
        "point": 5,
        "text": "Str",
        "feet": 11550
      },
      {
        "point": 6,
        "text": "Fin",
        "feet": 12210
      }
    ]
  },
  {
    "distance": "3 miles",
    "floor": 15840,
    "calls": [
      {
        "point": 1,
        "text": "1m",
        "feet": 5280
      },
      {
        "point": 2,
        "text": "11/2",
        "feet": 7920
      },
      {
        "point": 3,
        "text": "2m",
        "feet": 10560
      },
      {
        "point": 4,
        "text": "21/2",
        "feet": 13200
      },
      {
        "point": 5,
        "text": "Str",
        "feet": 15180
      },
      {
        "point": 6,
        "text": "Fin",
        "feet": 15840
      }
    ]
  },
  {
    "distance": "3 1/4 miles",
    "floor": 17160,
    "calls": [
      {
        "point": 1,
        "text": "1m",
        "feet": 5280
      },
      {
        "point": 2,
        "text": "2m",
        "feet": 10560
      },
      {
        "point": 3,
        "text": "21/2",
        "feet": 13200
      },
      {
        "point": 4,
        "text": "23/4",
        "feet": 14520
      },
      {
        "point": 5,
        "text": "Str",
        "feet": 16500
      },
      {
        "point": 6,
        "text": "Fin",
        "feet": 17160
      }
    ]
  },
  {
    "distance": "4 miles",
    "floor": 21120,
    "calls": [
      {
        "point": 1,
        "text": "1m",
        "feet": 5280
      },
      {
        "point": 2,
        "text": "2m",
        "feet": 10560
      },
      {
        "point": 3,
        "text": "3m",
        "feet": 15840
      },
      {
        "point": 4,
        "text": "31/2",
        "feet": 18480
      },
      {
        "point": 5,
        "text": "Str",
        "feet": 20460
      },
      {
        "point": 6,
        "text": "Fin",
        "feet": 21120
      }
    ]
  }
]

FRACTIONALS = [
  {
    "distance": "150 yards",
    "floor": 450,
    "fractionals": [
      {
        "point": 6,
        "text": "Fin",
        "feet": 450
      }
    ]
  },
  {
    "distance": "1 furlong",
    "floor": 660,
    "fractionals": [
      {
        "point": 6,
        "text": "Fin",
        "feet": 660
      }
    ]
  },
  {
    "distance": "2 furlongs",
    "floor": 1320,
    "fractionals": [
      {
        "point": 6,
        "text": "Fin",
        "feet": 1320
      }
    ]
  },
  {
    "distance": "2 1/2 furlongs",
    "floor": 1650,
    "fractionals": [
      {
        "point": 1,
        "text": "1/4",
        "feet": 1320
      },
      {
        "point": 6,
        "text": "Fin",
        "feet": 1650
      }
    ]
  },
  {
    "distance": "3 furlongs",
    "floor": 1980,
    "fractionals": [
      {
        "point": 1,
        "text": "1/4",
        "feet": 1320
      },
      {
        "point": 6,
        "text": "Fin",
        "feet": 1980
      }
    ]
  },
  {
    "distance": "3 1/2 furlongs",
    "floor": 2310,
    "fractionals": [
      {
        "point": 1,
        "text": "1/4",
        "feet": 1320
      },
      {
        "point": 2,
        "text": "3/8",
        "feet": 1980
      },
      {
        "point": 6,
        "text": "Fin",
        "feet": 2310
      }
    ]
  },
  {
    "distance": "3 3/4 furlongs",
    "floor": 2475,
    "fractionals": [
      {
        "point": 1,
        "text": "1/4",
        "feet": 1320
      },
      {
        "point": 6,
        "text": "Fin",
        "feet": 2475
      }
    ]
  },
  {
    "distance": "4 furlongs",
    "floor": 2640,
    "fractionals": [
      {
        "point": 1,
        "text": "1/4",
        "feet": 1320
      },
      {
        "point": 6,
        "text": "Fin",
        "feet": 2640
      }
    ]
  },
  {
    "distance": "4 1/2 furlongs",
    "floor": 2970,
    "fractionals": [
      {
        "point": 1,
        "text": "1/4",
        "feet": 1320
      },
      {
        "point": 2,
        "text": "1/2",
        "feet": 2640
      },
      {
        "point": 6,
        "text": "Fin",
        "feet": 2970
      }
    ]
  },
  {
    "distance": "5 furlongs",
    "floor": 3300,
    "fractionals": [
      {
        "point": 1,
        "text": "1/4",
        "feet": 1320
      },
      {
        "point": 2,
        "text": "1/2",
        "feet": 2640
      },
      {
        "point": 6,
        "text": "Fin",
        "feet": 3300
      }
    ]
  },
  {
    "distance": "5 1/4 furlongs",
    "floor": 3465,
    "fractionals": [
      {
        "point": 1,
        "text": "1/4",
        "feet": 1320
      },
      {
        "point": 2,
        "text": "1/2",
        "feet": 2640
      },
      {
        "point": 6,
        "text": "Fin",
        "feet": 3465
      }
    ]
  },
  {
    "distance": "5 1/2 furlongs",
    "floor": 3630,
    "fractionals": [
      {
        "point": 1,
        "text": "1/4",
        "feet": 1320
      },
      {
        "point": 2,
        "text": "1/2",
        "feet": 2640
      },
      {
        "point": 3,
        "text": "5/8",
        "feet": 3300
      },
      {
        "point": 6,
        "text": "Fin",
        "feet": 3630
      }
    ]
  },
  {
    "distance": "6 furlongs",
    "floor": 3960,
    "fractionals": [
      {
        "point": 1,
        "text": "1/4",
        "feet": 1320
      },
      {
        "point": 2,
        "text": "1/2",
        "feet": 2640
      },
      {
        "point": 3,
        "text": "5/8",
        "feet": 3300
      },
      {
        "point": 6,
        "text": "Fin",
        "feet": 3960
      }
    ]
  },
  {
    "distance": "6 1/2 furlongs",
    "floor": 4290,
    "fractionals": [
      {
        "point": 1,
        "text": "1/4",
        "feet": 1320
      },
      {
        "point": 2,
        "text": "1/2",
        "feet": 2640
      },
      {
        "point": 3,
        "text": "3/4",
        "feet": 3960
      },
      {
        "point": 6,
        "text": "Fin",
        "feet": 4290
      }
    ]
  },
  {
    "distance": "7 furlongs",
    "floor": 4620,
    "fractionals": [
      {
        "point": 1,
        "text": "1/4",
        "feet": 1320
      },
      {
        "point": 2,
        "text": "1/2",
        "feet": 2640
      },
      {
        "point": 3,
        "text": "3/4",
        "feet": 3960
      },
      {
        "point": 6,
        "text": "Fin",
        "feet": 4620
      }
    ]
  },
  {
    "distance": "7 1/2 furlongs",
    "floor": 4950,
    "fractionals": [
      {
        "point": 1,
        "text": "1/4",
        "feet": 1320
      },
      {
        "point": 2,
        "text": "1/2",
        "feet": 2640
      },
      {
        "point": 3,
        "text": "3/4",
        "feet": 3960
      },
      {
        "point": 6,
        "text": "Fin",
        "feet": 4950
      }
    ]
  },
  {
    "distance": "1 mile",
    "floor": 5280,
    "fractionals": [
      {
        "point": 1,
        "text": "1/4",
        "feet": 1320
      },
      {
        "point": 2,
        "text": "1/2",
        "feet": 2640
      },
      {
        "point": 3,
        "text": "3/4",
        "feet": 3960
      },
      {
        "point": 4,
        "text": "7/8",
        "feet": 4620
      },
      {
        "point": 6,
        "text": "Fin",
        "feet": 5280
      }
    ]
  },
  {
    "distance": "1 mile 40 yards",
    "floor": 5400,
    "fractionals": [
      {
        "point": 1,
        "text": "1/4",
        "feet": 1320
      },
      {
        "point": 2,
        "text": "1/2",
        "feet": 2640
      },
      {
        "point": 3,
        "text": "3/4",
        "feet": 3960
      },
      {
        "point": 4,
        "text": "1m",
        "feet": 5280
      },
      {
        "point": 6,
        "text": "Fin",
        "feet": 5400
      }
    ]
  },
  {
    "distance": "1 mile 70 yards",
    "floor": 5490,
    "fractionals": [
      {
        "point": 1,
        "text": "1/4",
        "feet": 1320
      },
      {
        "point": 2,
        "text": "1/2",
        "feet": 2640
      },
      {
        "point": 3,
        "text": "3/4",
        "feet": 3960
      },
      {
        "point": 4,
        "text": "1m",
        "feet": 5280
      },
      {
        "point": 6,
        "text": "Fin",
        "feet": 5490
      }
    ]
  },
  {
    "distance": "1 1/16 miles",
    "floor": 5610,
    "fractionals": [
      {
        "point": 1,
        "text": "1/4",
        "feet": 1320
      },
      {
        "point": 2,
        "text": "1/2",
        "feet": 2640
      },
      {
        "point": 3,
        "text": "3/4",
        "feet": 3960
      },
      {
        "point": 4,
        "text": "1m",
        "feet": 5280
      },
      {
        "point": 6,
        "text": "Fin",
        "feet": 5610
      }
    ]
  },
  {
    "distance": "1 1/8 miles",
    "floor": 5940,
    "fractionals": [
      {
        "point": 1,
        "text": "1/4",
        "feet": 1320
      },
      {
        "point": 2,
        "text": "1/2",
        "feet": 2640
      },
      {
        "point": 3,
        "text": "3/4",
        "feet": 3960
      },
      {
        "point": 4,
        "text": "1m",
        "feet": 5280
      },
      {
        "point": 6,
        "text": "Fin",
        "feet": 5940
      }
    ]
  },
  {
    "distance": "1 3/16 miles",
    "floor": 6270,
    "fractionals": [
      {
        "point": 1,
        "text": "1/4",
        "feet": 1320
      },
      {
        "point": 2,
        "text": "1/2",
        "feet": 2640
      },
      {
        "point": 3,
        "text": "3/4",
        "feet": 3960
      },
      {
        "point": 4,
        "text": "1m",
        "feet": 5280
      },
      {
        "point": 6,
        "text": "Fin",
        "feet": 6270
      }
    ]
  },
  {
    "distance": "1 1/4 miles",
    "floor": 6600,
    "fractionals": [
      {
        "point": 1,
        "text": "1/4",
        "feet": 1320
      },
      {
        "point": 2,
        "text": "1/2",
        "feet": 2640
      },
      {
        "point": 3,
        "text": "3/4",
        "feet": 3960
      },
      {
        "point": 4,
        "text": "1m",
        "feet": 5280
      },
      {
        "point": 6,
        "text": "Fin",
        "feet": 6600
      }
    ]
  },
  {
    "distance": "1 5/16 miles",
    "floor": 6930,
    "fractionals": [
      {
        "point": 1,
        "text": "1/4",
        "feet": 1320
      },
      {
        "point": 2,
        "text": "1/2",
        "feet": 2640
      },
      {
        "point": 3,
        "text": "3/4",
        "feet": 3960
      },
      {
        "point": 4,
        "text": "1m",
        "feet": 5280
      },
      {
        "point": 6,
        "text": "Fin",
        "feet": 6930
      }
    ]
  },
  {
    "distance": "1 3/8 miles",
    "floor": 7260,
    "fractionals": [
      {
        "point": 1,
        "text": "1/4",
        "feet": 1320
      },
      {
        "point": 2,
        "text": "1/2",
        "feet": 2640
      },
      {
        "point": 3,
        "text": "3/4",
        "feet": 3960
      },
      {
        "point": 4,
        "text": "1m",
        "feet": 5280
      },
      {
        "point": 5,
        "text": "1 1/4m",
        "feet": 6600
      },
      {
        "point": 6,
        "text": "Fin",
        "feet": 7260
      }
    ]
  },
  {
    "distance": "1 7/16 miles",
    "floor": 7590,
    "fractionals": [
      {
        "point": 1,
        "text": "1/4",
        "feet": 1320
      },
      {
        "point": 2,
        "text": "1/2",
        "feet": 2640
      },
      {
        "point": 3,
        "text": "3/4",
        "feet": 3960
      },
      {
        "point": 4,
        "text": "1m",
        "feet": 5280
      },
      {
        "point": 5,
        "text": "1 1/4m",
        "feet": 6600
      },
      {
        "point": 6,
        "text": "Fin",
        "feet": 7590
      }
    ]
  },
  {
    "distance": "1 1/2 miles",
    "floor": 7920,
    "fractionals": [
      {
        "point": 1,
        "text": "1/4",
        "feet": 1320
      },
      {
        "point": 2,
        "text": "1/2",
        "feet": 2640
      },
      {
        "point": 3,
        "text": "3/4",
        "feet": 3960
      },
      {
        "point": 4,
        "text": "1m",
        "feet": 5280
      },
      {
        "point": 5,
        "text": "1 1/4m",
        "feet": 6600
      },
      {
        "point": 6,
        "text": "Fin",
        "feet": 7920
      }
    ]
  },
  {
    "distance": "1 9/16 miles",
    "floor": 8250,
    "fractionals": [
      {
        "point": 1,
        "text": "1/4",
        "feet": 1320
      },
      {
        "point": 2,
        "text": "1/2",
        "feet": 2640
      },
      {
        "point": 3,
        "text": "3/4",
        "feet": 3960
      },
      {
        "point": 4,
        "text": "1m",
        "feet": 5280
      },
      {
        "point": 5,
        "text": "1 1/4m",
        "feet": 6600
      },
      {
        "point": 6,
        "text": "Fin",
        "feet": 8250
      }
    ]
  },
  {
    "distance": "1 5/8 miles",
    "floor": 8580,
    "fractionals": [
      {
        "point": 1,
        "text": "1/2",
        "feet": 2640
      },
      {
        "point": 2,
        "text": "3/4",
        "feet": 3960
      },
      {
        "point": 3,
        "text": "1m",
        "feet": 5280
      },
      {
        "point": 4,
        "text": "1 1/4m",
        "feet": 6600
      },
      {
        "point": 5,
        "text": "1 1/2m",
        "feet": 7920
      },
      {
        "point": 6,
        "text": "Fin",
        "feet": 8580
      }
    ]
  },
  {
    "distance": "1 11/16 miles",
    "floor": 8910,
    "fractionals": [
      {
        "point": 1,
        "text": "1/2",
        "feet": 2640
      },
      {
        "point": 2,
        "text": "3/4",
        "feet": 3960
      },
      {
        "point": 3,
        "text": "1m",
        "feet": 5280
      },
      {
        "point": 4,
        "text": "1 1/4m",
        "feet": 6600
      },
      {
        "point": 5,
        "text": "1 1/2m",
        "feet": 7920
      },
      {
        "point": 6,
        "text": "Fin",
        "feet": 8910
      }
    ]
  },
  {
    "distance": "1 3/4 miles",
    "floor": 9240,
    "fractionals": [
      {
        "point": 1,
        "text": "1/2",
        "feet": 2640
      },
      {
        "point": 2,
        "text": "3/4",
        "feet": 3960
      },
      {
        "point": 3,
        "text": "1m",
        "feet": 5280
      },
      {
        "point": 4,
        "text": "1 1/4m",
        "feet": 6600
      },
      {
        "point": 5,
        "text": "1 1/2m",
        "feet": 7920
      },
      {
        "point": 6,
        "text": "Fin",
        "feet": 9240
      }
    ]
  },
  {
    "distance": "1 13/16 miles",
    "floor": 9570,
    "fractionals": [
      {
        "point": 1,
        "text": "1/2",
        "feet": 2640
      },
      {
        "point": 2,
        "text": "1m",
        "feet": 5280
      },
      {
        "point": 3,
        "text": "1 1/4m",
        "feet": 6600
      },
      {
        "point": 4,
        "text": "1 1/2m",
        "feet": 7920
      },
      {
        "point": 5,
        "text": "1 3/4m",
        "feet": 9240
      },
      {
        "point": 6,
        "text": "Fin",
        "feet": 9570
      }
    ]
  },
  {
    "distance": "1 7/8 miles",
    "floor": 9900,
    "fractionals": [
      {
        "point": 1,
        "text": "1/2",
        "feet": 2640
      },
      {
        "point": 2,
        "text": "1m",
        "feet": 5280
      },
      {
        "point": 3,
        "text": "1 1/4m",
        "feet": 6600
      },
      {
        "point": 4,
        "text": "1 1/2m",
        "feet": 7920
      },
      {
        "point": 5,
        "text": "1 3/4m",
        "feet": 9240
      },
      {
        "point": 6,
        "text": "Fin",
        "feet": 9900
      }
    ]
  },
  {
    "distance": "1 15/16 miles",
    "floor": 10230,
    "fractionals": [
      {
        "point": 1,
        "text": "1/2",
        "feet": 2640
      },
      {
        "point": 2,
        "text": "1m",
        "feet": 5280
      },
      {
        "point": 3,
        "text": "1 1/4m",
        "feet": 6600
      },
      {
        "point": 4,
        "text": "1 1/2m",
        "feet": 7920
      },
      {
        "point": 5,
        "text": "1 3/4m",
        "feet": 9240
      },
      {
        "point": 6,
        "text": "Fin",
        "feet": 10230
      }
    ]
  },
  {
    "distance": "2 miles",
    "floor": 10560,
    "fractionals": [
      {
        "point": 1,
        "text": "1/2",
        "feet": 2640
      },
      {
        "point": 2,
        "text": "1m",
        "feet": 5280
      },
      {
        "point": 3,
        "text": "1 1/4m",
        "feet": 6600
      },
      {
        "point": 4,
        "text": "1 1/2m",
        "feet": 7920
      },
      {
        "point": 5,
        "text": "1 3/4m",
        "feet": 9240
      },
      {
        "point": 6,
        "text": "Fin",
        "feet": 10560
      }
    ]
  },
  {
    "distance": "2 miles 40 yards",
    "floor": 10680,
    "fractionals": [
      {
        "point": 1,
        "text": "1/2",
        "feet": 2640
      },
      {
        "point": 2,
        "text": "1m",
        "feet": 5280
      },
      {
        "point": 3,
        "text": "1 1/2m",
        "feet": 7920
      },
      {
        "point": 4,
        "text": "1 3/4m",
        "feet": 9240
      },
      {
        "point": 5,
        "text": "2m",
        "feet": 10560
      },
      {
        "point": 6,
        "text": "Fin",
        "feet": 10680
      }
    ]
  },
  {
    "distance": "2 miles 70 yards",
    "floor": 10770,
    "fractionals": [
      {
        "point": 1,
        "text": "1/2",
        "feet": 2640
      },
      {
        "point": 2,
        "text": "1m",
        "feet": 5280
      },
      {
        "point": 3,
        "text": "1 1/2m",
        "feet": 7920
      },
      {
        "point": 4,
        "text": "1 3/4m",
        "feet": 9240
      },
      {
        "point": 5,
        "text": "2m",
        "feet": 10560
      },
      {
        "point": 6,
        "text": "Fin",
        "feet": 10770
      }
    ]
  },
  {
    "distance": "2 1/16 miles",
    "floor": 10890,
    "fractionals": [
      {
        "point": 1,
        "text": "1/2",
        "feet": 2640
      },
      {
        "point": 2,
        "text": "1m",
        "feet": 5280
      },
      {
        "point": 3,
        "text": "1 1/2m",
        "feet": 7920
      },
      {
        "point": 4,
        "text": "1 3/4m",
        "feet": 9240
      },
      {
        "point": 5,
        "text": "2m",
        "feet": 10560
      },
      {
        "point": 6,
        "text": "Fin",
        "feet": 10890
      }
    ]
  },
  {
    "distance": "2 1/8 miles",
    "floor": 11220,
    "fractionals": [
      {
        "point": 1,
        "text": "1/2",
        "feet": 2640
      },
      {
        "point": 2,
        "text": "1m",
        "feet": 5280
      },
      {
        "point": 3,
        "text": "1 1/2m",
        "feet": 7920
      },
      {
        "point": 4,
        "text": "1 3/4m",
        "feet": 9240
      },
      {
        "point": 5,
        "text": "2m",
        "feet": 10560
      },
      {
        "point": 6,
        "text": "Fin",
        "feet": 11220
      }
    ]
  },
  {
    "distance": "2 3/16 miles",
    "floor": 11550,
    "fractionals": [
      {
        "point": 1,
        "text": "1/2",
        "feet": 2640
      },
      {
        "point": 2,
        "text": "1m",
        "feet": 5280
      },
      {
        "point": 3,
        "text": "1 1/2m",
        "feet": 7920
      },
      {
        "point": 4,
        "text": "1 3/4m",
        "feet": 9240
      },
      {
        "point": 5,
        "text": "2m",
        "feet": 10560
      },
      {
        "point": 6,
        "text": "Fin",
        "feet": 11550
      }
    ]
  }
]