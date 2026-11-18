package com.example.myapplication.adapter;

import android.content.Context;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.BaseAdapter;
import androidx.core.content.ContextCompat;

import com.example.myapplication.R;
import com.example.myapplication.databinding.ItemAppointmentBinding;
import com.example.myapplication.model.Appointment;
import com.example.myapplication.util.AppointmentDateTime;

import java.util.ArrayList;

public class AppointmentAdapter extends BaseAdapter {
    private final LayoutInflater inflater;
    private ArrayList<Appointment> appointments;

    public AppointmentAdapter(Context context, ArrayList<Appointment> appointments) {
        inflater = LayoutInflater.from(context);
        this.appointments = appointments;
    }

    public void updateData(ArrayList<Appointment> appointments) {
        this.appointments = appointments;
        notifyDataSetChanged();
    }

    @Override public int getCount() { return appointments.size(); }
    @Override public Appointment getItem(int position) { return appointments.get(position); }
    @Override public long getItemId(int position) { return getItem(position).getId(); }
    @Override public boolean hasStableIds() { return true; }

    @Override
    public View getView(int position, View convertView, ViewGroup parent) {
        ItemAppointmentBinding holder;
        if (convertView == null) {
            holder = ItemAppointmentBinding.inflate(inflater, parent, false);
            convertView = holder.getRoot();
            convertView.setTag(holder);
        } else {
            holder = (ItemAppointmentBinding) convertView.getTag();
        }
        Appointment appointment = getItem(position);
        holder.tvItemTitle.setText(appointment.getTitle());
        holder.tvItemLocation.setText(appointment.getLocation());
        holder.tvItemDateTime.setText(AppointmentDateTime.format(appointment.getDate(), appointment.getTime()));
        holder.tvItemReminder.setText(appointment.isReminder()
                ? R.string.has_reminder : R.string.no_reminder);
        holder.tvItemReminder.setBackgroundResource(appointment.isReminder()
                ? R.drawable.ap_chip_on : R.drawable.ap_chip_off);
        holder.tvItemReminder.setTextColor(ContextCompat.getColor(parent.getContext(),
                appointment.isReminder() ? R.color.ap_primary : R.color.ap_muted));
        return convertView;
    }
}
