#ifndef SCALER_PARAMS_H
#define SCALER_PARAMS_H

#define NUM_FEATURES 11

// Feature order (must match model input order)
// 0  temp_avg
// 1  temp_max
// 2  temp_min
// 3  temp_rate
// 4  time_outside_range_sec
// 5  humidity_avg
// 6  humidity_variance
// 7  humidity_spike_count
// 8  door_open_count
// 9  door_open_duration_sec
// 10 max_door_open_time_sec

static const float MEAN[NUM_FEATURES] = {
  7.210144f,
  8.169319f,
  6.520216f,
  0.282069f,
  147.218099f,
  62.261628f,
  3.275677f,
  1.482821f,
  2.331795f,
  105.826410f,
  92.498416f
};

static const float STD[NUM_FEATURES] = {
  2.514610f,
  3.266713f,
  2.073003f,
  0.262767f,
  174.662788f,
  7.221099f,
  1.588952f,
  1.110307f,
  2.080474f,
  116.317368f,
  105.984297f
};

#endif // SCALER_PARAMS_H
