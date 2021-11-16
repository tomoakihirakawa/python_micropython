# try:
#     # microptyhonの場合
#     from machine import SoftI2C as I2C
#     from machine import Pin
#     import ustruct as struct
#     from utime import sleep
#     _MicroPython_ = True

#     # https://docs.micropython.org/en/latest/library/machine.I2C.html
#     """
#     I2C.write(buf)                            スレーブ自身に１バイトの値を書き込む
#     I2C.writeto(addr, buf, stop=True, /)      スレーブ内部のレジスターに数バイトの値を書き込む
#     writeto_mem                               スレーブ内部のレジスターにブロックバイトの値を書き込む 
#     """

#     def write_byte(bus, address, value):        
#         # bus.writeto(address, struct.pack("<8b", value))
#         bus.writeto(address, struct.pack("<b", value))        

#     def write_byte_data(bus, address, register, value):
#         bus.writeto_mem(address, register, bytearray([value]))

#     def read_byte_data(bus, address, register, n=2):
#         buf = bus.readfrom_mem(address, register, n)
#         return struct.unpack("<" + str(n) + "b", buf)  # アンパックしたタプル

# except:

#     """
#     write_byte           スレーブ自身に１バイトの値を書き込む
#     write_byte_data      スレーブ内部のレジスターに１バイトの値を書き込む
#     write_i2c_block_data スレーブ内部のレジスターにブロックバイトの値を書き込む    
#     """

#     # ラズパイの場合
#     try:
#         import smbus
#         from time import sleep
#         _MicroPython_ = False

#         def write_byte(bus, address, value):
#             bus.write_byte(address, value)

#         def write_byte_data(bus, address, register, value):
#             bus.write_byte_data(address, register, value)

#         def read_byte_data(bus, address, register, n=2):
#             return bus.read_i2c_block_data(address, register, n)

#     except:
#         print("\u001b[35m")
#         print('please install smbus')
#         print("\u001b[0m")

try:
    # microptyhonの場合
    from machine import SoftI2C as I2C
    from machine import Pin
    import ustruct as struct
    from utime import sleep
    _MicroPython_ = True

    # https://docs.micropython.org/en/latest/library/machine.I2C.html
    """
    I2C.write(buf)                            スレーブ自身に１バイトの値を書き込む
    I2C.writeto(addr, buf, stop=True, /)      スレーブ内部のレジスターに数バイトの値を書き込む
    writeto_mem                               スレーブ内部のレジスターにブロックバイトの値を書き込む 
    """

    def write_byte(bus, address, value):        
        bus.writeto(address, bytearray([value]))        
        
    def write_byte_data(bus, address, register, value):
        bus.writeto_mem(address, register, bytearray([value]))

    def read_byte(bus, address, nbytes=2):
        return bus.readfrom(address, nbytes)  # アンパックしたタプル

    def read_byte_data(bus, address, register, nbytes=2):
        return bus.readfrom_mem(address, register, nbytes)

except:

    """
    write_byte           スレーブ自身に１バイトの値を書き込む
    write_byte_data      スレーブ内部のレジスターに１バイトの値を書き込む
    write_i2c_block_data スレーブ内部のレジスターにブロックバイトの値を書き込む    
    """

    # ラズパイの場合
    try:
        import smbus
        from time import sleep
        _MicroPython_ = False

        def write_byte(bus, address, value):
            bus.write_byte(address, value)

        def write_byte_data(bus, address, register, value):
            bus.write_byte_data(address, register, value)

        def read_byte(bus, address, nbytes=2):
            return bus.read_byte(address, nbytes)

        def read_byte_data(bus, address, register, nbytes=2):
            return bus.read_i2c_block_data(address, register, nbytes)

    except:
        print("\u001b[35m")
        print('please install smbus')
        print("\u001b[0m")
