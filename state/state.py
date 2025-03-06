from aiogram.fsm.state import State, StatesGroup

class BookingProcces(StatesGroup):
    choosing_date = State()
    choosing_time = State()
    set_quantity_of_guests = State()
    set_preferences = State()
    confirm_booking = State()
    get_name_surname = State()
    waiting_for_payment = State()

class CheckingDateProcess(StatesGroup):
    set_date = State()
    set_time = State()


class CancellingProccess(StatesGroup):
    choosing_id = State()



