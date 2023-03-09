# LIS35DE register map, according to:
# https://github.com/krzychb/esp-lis35de/blob/master/components/lis35de/lis35de.c

READ_INC          = 0x80

REG_OUTX          = 0x29    # OUT_X (29h) register
REG_OUTY          = 0x2B    # OUT_Y (2Bh) register
REG_OUTZ          = 0x2D    # OUT_Z (2Dh) register

REG_CR1           = 0x20    # CTRL_REG1 (20h) register
REG_CR1_XEN       = 0x1     # X axis enable. Default value: 1
REG_CR1_YEN       = 0x2     # Y axis enable. Default value: 1
REG_CR1_ZEN       = 0x4     # Z axis enable. Default value: 1
REG_CR1_DR_400HZ  = 0x80    # Data rate selection. Default value: 0
REG_CR1_ACTIVE    = 0x40    # Power Down Control. Default value: 0
REG_CR1_FULL_SCALE = 0x20   # Full Scale selection. Default value: 0

REG_CR2           = 0x21
REG_CR2_BOOT      = 0x40

CR3               = 0x22
CR3_IHL           = 0x80
CR3_CLICK_INT     = 0x7
CR3_FF1_INT       = 0x1

FF_WU_CFG_1       = 0x30
FF_WU_SRC_1       = 0x31
FF_WU_THS_1       = 0x32
FF_WU_DURATION_1  = 0x33

CLICK_CFG         = 0x38
CLICK_THSY_X      = 0x3b
CLICK_THSZ        = 0x3c
CLICK_TIME_LIMIT  = 0x3D

STATUS_REG        = 0x27

I2C_ADDR          = (0x38>>1)