package com.example.myapplication;

import static org.junit.Assert.assertEquals;
import com.example.myapplication.util.AppointmentDateTime;
import org.junit.Test;

public class AppointmentDateTimeTest {
    @Test public void formatsStoredDateForListAndDetail() {
        assertEquals("25/10/2026 · 09:00", AppointmentDateTime.format("2026-10-25", "09:00"));
        assertEquals("29/02/2028 · 00:05", AppointmentDateTime.format("2028-02-29", "00:05"));
    }

    @Test public void malformedDateDoesNotCrashScreen() {
        assertEquals("2026-02-30 · 10:00", AppointmentDateTime.format("2026-02-30", "10:00"));
    }
}
