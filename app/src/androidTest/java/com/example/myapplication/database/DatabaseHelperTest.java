package com.example.myapplication.database;

import static org.junit.Assert.*;

import android.content.Context;
import android.database.sqlite.SQLiteConstraintException;
import androidx.test.ext.junit.runners.AndroidJUnit4;
import androidx.test.platform.app.InstrumentationRegistry;
import com.example.myapplication.model.Appointment;
import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import java.util.ArrayList;

@RunWith(AndroidJUnit4.class)
public class DatabaseHelperTest {
    private static final String TEST_DB = "appointments-instrumentation-test.db";
    private Context context;
    private DatabaseHelper database;

    @Before public void setUp() {
        context = InstrumentationRegistry.getInstrumentation().getTargetContext();
        context.deleteDatabase(TEST_DB);
        database = new DatabaseHelper(context, TEST_DB);
    }

    @After public void tearDown() {
        database.close();
        context.deleteDatabase(TEST_DB);
    }

    @Test public void seedAndLogin_useDatabaseAndBoundParameters() {
        assertEquals(3, database.countAll());
        assertEquals(2, database.countReminders());
        assertEquals("Họp nhóm đồ án", database.getAllAppointments().get(0).getTitle());
        assertTrue(database.checkLogin("admin", "123456"));
        assertFalse(database.checkLogin("admin", "wrong"));
        assertFalse(database.checkLogin("' OR 1=1 --", "123456"));
        database.insertUser("o'brien", "a'b");
        assertTrue(database.checkLogin("o'brien", "a'b"));
    }

    @Test(expected = SQLiteConstraintException.class)
    public void usernamesAreUnique() {
        database.insertUser("admin", "another-password");
    }

    @Test public void mutationsUpdateCountsAndPersistAfterReopen() {
        int id = (int) database.insertAppointment(new Appointment(
                "Hẹn O'Brien", "Phòng 'A'", "2030-01-02", "08:05", false));
        assertTrue(id > 0);
        assertEquals(4, database.countAll());
        assertEquals(2, database.countReminders());
        database.updateReminder(id, true);
        assertEquals(3, database.countReminders());
        database.close();
        database = new DatabaseHelper(context, TEST_DB);
        Appointment reloaded = database.getAppointmentById(id);
        assertNotNull(reloaded);
        assertEquals("Hẹn O'Brien", reloaded.getTitle());
        assertEquals("2030-01-02", reloaded.getDate());
        assertEquals("08:05", reloaded.getTime());
        assertTrue(reloaded.isReminder());
        assertEquals(4, database.countAll());
        database.updateReminder(id, false);
        assertEquals(2, database.countReminders());
        database.deleteAppointment(id);
        assertNull(database.getAppointmentById(id));
        assertEquals(3, database.countAll());
        database.close();
        database = new DatabaseHelper(context, TEST_DB);
        assertNull(database.getAppointmentById(id));
        assertEquals(3, database.countAll());
    }

    @Test public void orderingUsesDateThenTimeAndHandlesMissingIds() {
        int later = (int) database.insertAppointment(new Appointment("Sau", "A", "2030-01-01", "10:00", false));
        int earlier = (int) database.insertAppointment(new Appointment("Trước", "A", "2030-01-01", "09:00", false));
        ArrayList<Appointment> appointments = database.getAllAppointments();
        assertEquals(earlier, appointments.get(3).getId());
        assertEquals(later, appointments.get(4).getId());
        assertNull(database.getAppointmentById(-1));
        database.updateReminder(-1, true);
        database.deleteAppointment(-1);
        assertEquals(5, database.countAll());
        assertEquals(2, database.countReminders());
    }
}
