package com.example.myapplication.util;

import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.Locale;

public final class AppointmentDateTime {
    private AppointmentDateTime() { }

    public static String format(String date, String time) {
        SimpleDateFormat storage = new SimpleDateFormat("yyyy-MM-dd HH:mm", Locale.ROOT);
        storage.setLenient(false);
        try {
            Date parsed = storage.parse(date + " " + time);
            if (parsed != null) {
                return new SimpleDateFormat("dd/MM/yyyy · HH:mm", Locale.ROOT).format(parsed);
            }
        } catch (ParseException ignored) {
            // Keep a malformed imported value readable instead of crashing the list.
        }
        return date + " · " + time;
    }
}
